import csv
import os
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from results.models import RaceDayResult
from riders.models import Rider
from races.models import RaceDay, RaceParticipation


class Command(BaseCommand):
    help = 'Import race day results from structured directories (results-by-race-day/race_day-X/*.csv) and create race participations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-dir',
            type=str,
            default='input_data/results-by-race-day',
            help='Base directory containing race_day-X folders (default: input_data/results-by-race-day)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually creating results in the database'
        )

    def normalize_name(self, name):
        """Normalize name for comparison (lowercase, strip)"""
        return name.strip().lower()
    
    def map_category(self, filename):
        """
        Map CSV filename to valid category choice.
        Examples:
        - 'pro.csv' or 'profi.csv' -> 'profi'
        - 'expert.csv' -> 'expert'
        - 'senior_40.csv' -> 'seniors_40'
        - 'senior_50.csv' -> 'seniors_50'
        """
        category = filename.replace('.csv', '').replace('_processed', '').lower()
        
        # Map variations to valid choices
        category_map = {
            'pro': 'profi',
            'profi': 'profi',
            'expert': 'expert',
            'junior': 'junior',
            'standard': 'standard',
            'standard_junior': 'standard_junior',
            'senior_40': 'seniors_40',
            'seniors_40': 'seniors_40',
            'senior_50': 'seniors_50',
            'seniors_50': 'seniors_50',
            'women': 'women',
        }
        
        return category_map.get(category, category)

    def find_rider(self, first_name, last_name, license_number):
        """
        Find rider by matching first name, last name, and license number.
        Returns the rider or None if not found.
        """
        # Normalize names for comparison
        first_normalized = self.normalize_name(first_name)
        last_normalized = self.normalize_name(last_name)
        license_str = str(license_number).strip()
        
        # Try to find rider with matching license number
        riders = Rider.objects.filter(license_number=license_str)
        
        for rider in riders:
            rider_first = self.normalize_name(rider.first_name)
            rider_last = self.normalize_name(rider.last_name)
            
            # Check if names match
            if rider_first == first_normalized and rider_last == last_normalized:
                return rider
        
        # If not found by license, try by name only (in case license number differs)
        riders_by_name = Rider.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name
        )
        
        if riders_by_name.count() == 1:
            rider = riders_by_name.first()
            self.stdout.write(
                self.style.WARNING(
                    f'Found rider by name only: {rider.full_name} (license mismatch: CSV={license_str}, DB={rider.license_number})'
                )
            )
            return rider
        
        return None

    def handle(self, *args, **options):
        base_dir_path = options['base_dir']
        dry_run = options['dry_run']
        
        # Build the full path
        if os.path.isabs(base_dir_path):
            base_dir = base_dir_path
        elif os.path.exists(base_dir_path):
            base_dir = base_dir_path
        else:
            # Try different base paths
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            
            # Try: /app/input_data/... (Docker)
            base_dir = os.path.join('/app', base_dir_path)
            if not os.path.exists(base_dir):
                # Try: bgx-api/../input_data/... (local)
                project_root = os.path.dirname(app_dir)
                base_dir = os.path.join(project_root, base_dir_path)
            if not os.path.exists(base_dir):
                # Try: bgx-api/input_data/... (local alternative)
                base_dir = os.path.join(app_dir, base_dir_path)
        
        if not os.path.exists(base_dir):
            self.stdout.write(self.style.ERROR(f'Base directory not found: {base_dir}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Scanning directory: {base_dir}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made to the database'))
        
        total_created = 0
        total_updated = 0
        total_skipped = 0
        total_errors = 0
        total_participations_created = 0
        total_participations_updated = 0
        race_days_processed = 0
        files_processed = 0
        
        # Find all race_day-X directories
        try:
            entries = os.listdir(base_dir)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading directory: {str(e)}'))
            return
        
        race_day_dirs = sorted([d for d in entries if re.match(r'race_day-\d+', d)])
        
        if not race_day_dirs:
            self.stdout.write(self.style.ERROR('No race_day-X directories found!'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(race_day_dirs)} race day directories'))
        
        # Process each race day directory
        for race_day_dir in race_day_dirs:
            # Extract race day ID
            match = re.search(r'race_day-(\d+)', race_day_dir)
            if not match:
                continue
            
            race_day_id = match.group(1)
            race_day_path = os.path.join(base_dir, race_day_dir)
            
            # Find race day in database
            try:
                race_day = RaceDay.objects.get(id=race_day_id)
            except RaceDay.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Race day not found in database: ID {race_day_id} - Skipping directory')
                )
                continue
            
            self.stdout.write(self.style.SUCCESS(f'\n{"=" * 70}'))
            self.stdout.write(self.style.SUCCESS(f'Processing: {race_day_dir} -> {race_day}'))
            self.stdout.write(self.style.SUCCESS(f'{"=" * 70}'))
            
            race_days_processed += 1
            
            # Find all CSV files in this directory
            try:
                csv_files = [f for f in os.listdir(race_day_path) if f.endswith('.csv')]
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error reading directory {race_day_path}: {str(e)}'))
                continue
            
            if not csv_files:
                self.stdout.write(self.style.WARNING(f'No CSV files found in {race_day_dir}'))
                continue
            
            # Get the race from the race day
            race = race_day.race
            
            # Process each CSV file
            for csv_file in sorted(csv_files):
                csv_path = os.path.join(race_day_path, csv_file)
                category = self.map_category(csv_file)
                
                self.stdout.write(f'\n  Reading: {csv_file} (category: {category})')
                
                files_processed += 1
                file_created = 0
                file_updated = 0
                file_skipped = 0
                file_errors = 0
                
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        
                        for row in reader:
                            race_number = row.get('RaceNumber', '').strip()
                            first_name = row.get('FirstName', '').strip()
                            last_name = row.get('LastName', '').strip()
                            position_str = row.get('Position', '').strip()
                            points_str = row.get('Points', '').strip()
                            
                            if not race_number or not first_name or not last_name:
                                self.stdout.write(
                                    self.style.WARNING(f'    Skipping incomplete row: {row}')
                                )
                                file_skipped += 1
                                continue
                            
                            # Convert position and points
                            try:
                                position = int(position_str) if position_str else 0
                            except ValueError:
                                self.stdout.write(
                                    self.style.WARNING(f'    Invalid position for {first_name} {last_name}: {position_str}')
                                )
                                position = 0
                            
                            try:
                                points = float(points_str) if points_str else 0.0
                            except ValueError:
                                self.stdout.write(
                                    self.style.WARNING(f'    Invalid points for {first_name} {last_name}: {points_str}')
                                )
                                points = 0.0
                            
                            # Find rider
                            rider = self.find_rider(first_name, last_name, race_number)
                            
                            if not rider:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'    Rider not found: {first_name} {last_name} (License: {race_number})'
                                    )
                                )
                                file_skipped += 1
                                continue
                            
                            if dry_run:
                                self.stdout.write(
                                    f'    Would create: {rider.full_name} - P{position} - {points} pts + participation'
                                )
                                file_created += 1
                            else:
                                try:
                                    with transaction.atomic():
                                        # Create race participation
                                        participation, part_created = RaceParticipation.objects.update_or_create(
                                            race=race,
                                            rider=rider,
                                            defaults={
                                                'category': category,
                                                'status': 'confirmed',
                                                'bib_number': race_number,
                                            }
                                        )
                                        
                                        if part_created:
                                            total_participations_created += 1
                                        else:
                                            total_participations_updated += 1
                                        
                                        # Create race day result
                                        result, created = RaceDayResult.objects.update_or_create(
                                            race_day=race_day,
                                            rider=rider,
                                            defaults={
                                                'position': position,
                                                'points_earned': points,
                                            }
                                        )
                                        
                                        if created:
                                            file_created += 1
                                            action = '✓ Created'
                                        else:
                                            file_updated += 1
                                            action = '↻ Updated'
                                        
                                        part_status = '(new)' if part_created else '(exists)'
                                        self.stdout.write(
                                            f'    {action}: {rider.full_name} - P{position} - {points} pts - {category} {part_status}'
                                        )
                                        
                                except Exception as e:
                                    self.stdout.write(
                                        self.style.ERROR(
                                            f'    Error creating result for {first_name} {last_name}: {str(e)}'
                                        )
                                    )
                                    file_errors += 1
                    
                    # File summary
                    self.stdout.write(f'  {csv_file}: Created={file_created}, Updated={file_updated}, Skipped={file_skipped}, Errors={file_errors}')
                    
                    total_created += file_created
                    total_updated += file_updated
                    total_skipped += file_skipped
                    total_errors += file_errors
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error reading {csv_file}: {str(e)}'))
                    total_errors += 1
        
        # Final summary
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 70}'))
        self.stdout.write(self.style.SUCCESS(f'IMPORT COMPLETED!'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 70}'))
        self.stdout.write(self.style.SUCCESS(f'Race day directories processed: {race_days_processed}'))
        self.stdout.write(self.style.SUCCESS(f'CSV files processed: {files_processed}'))
        self.stdout.write(self.style.SUCCESS(f''))
        self.stdout.write(self.style.SUCCESS(f'Race Day Results:'))
        self.stdout.write(self.style.SUCCESS(f'  Created: {total_created}'))
        self.stdout.write(self.style.SUCCESS(f'  Updated: {total_updated}'))
        self.stdout.write(self.style.SUCCESS(f''))
        self.stdout.write(self.style.SUCCESS(f'Race Participations:'))
        self.stdout.write(self.style.SUCCESS(f'  Created: {total_participations_created}'))
        self.stdout.write(self.style.SUCCESS(f'  Updated: {total_participations_updated}'))
        if total_skipped > 0:
            self.stdout.write(self.style.WARNING(f''))
            self.stdout.write(self.style.WARNING(f'Skipped: {total_skipped}'))
        if total_errors > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {total_errors}'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 70}'))

