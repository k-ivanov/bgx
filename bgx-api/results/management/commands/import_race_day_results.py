import csv
import os
import re
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from results.models import RaceDayResult
from riders.models import Rider
from races.models import RaceDay


User = get_user_model()


class Command(BaseCommand):
    help = 'Import race day results from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='input_data/user_racers/pro_processed.csv',
            help='Path to the CSV file (default: input_data/user_racers/pro_processed.csv)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually creating results in the database'
        )
        parser.add_argument(
            '--category',
            type=str,
            default='profi',
            help='Category name for these results (default: profi)'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        dry_run = options['dry_run']
        category = options['category']
        
        # Build the full path
        if os.path.isabs(csv_file):
            file_path = csv_file
        elif os.path.exists(csv_file):
            file_path = csv_file
        else:
            # Try different base paths
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            
            # Try: /app/input_data/... (Docker)
            file_path = os.path.join('/app', csv_file)
            if not os.path.exists(file_path):
                # Try: bgx-api/../input_data/... (local)
                project_root = os.path.dirname(base_dir)
                file_path = os.path.join(project_root, csv_file)
            if not os.path.exists(file_path):
                # Try: bgx-api/input_data/... (local alternative)
                file_path = os.path.join(base_dir, csv_file)
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            self.stdout.write(self.style.ERROR(f'Searched in multiple locations. Please check the file path.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Reading results from: {file_path}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made to the database'))
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        rider_not_found = []
        race_day_not_found = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Find all race_day columns
            race_day_columns = [col for col in reader.fieldnames if col.startswith('race_day-')]
            
            if not race_day_columns:
                self.stdout.write(self.style.ERROR('No race_day columns found in CSV!'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Found {len(race_day_columns)} race day columns: {race_day_columns}'))
            
            for row in reader:
                username = row.get('username', '').strip()
                position_str = row.get('N', '').strip()
                
                if not username:
                    self.stdout.write(self.style.WARNING(f'Skipping row with no username'))
                    skipped_count += 1
                    continue
                
                # Convert position to integer
                try:
                    position = int(position_str) if position_str else 0
                except ValueError:
                    self.stdout.write(self.style.WARNING(f'Invalid position for {username}: {position_str}'))
                    position = 0
                
                # Find rider by username
                try:
                    user = User.objects.get(username=username)
                    rider = user.rider_profile
                except User.DoesNotExist:
                    if username not in rider_not_found:
                        self.stdout.write(self.style.WARNING(f'User not found: {username}'))
                        rider_not_found.append(username)
                    skipped_count += 1
                    continue
                except Rider.DoesNotExist:
                    if username not in rider_not_found:
                        self.stdout.write(self.style.WARNING(f'Rider profile not found for user: {username}'))
                        rider_not_found.append(username)
                    skipped_count += 1
                    continue
                
                # Process each race day column
                for col in race_day_columns:
                    points_str = row.get(col, '').strip()
                    
                    # Skip if no points (empty or missing)
                    if not points_str:
                        continue
                    
                    # Extract race day ID from column name (e.g., "race_day-1" -> "1")
                    match = re.search(r'race_day-(\d+)', col)
                    if not match:
                        self.stdout.write(self.style.WARNING(f'Could not parse race day ID from column: {col}'))
                        continue
                    
                    race_day_id = match.group(1)
                    
                    # Convert points to decimal
                    try:
                        points = float(points_str)
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f'Invalid points for {username} on {col}: {points_str}'))
                        continue
                    
                    # Find race day
                    try:
                        race_day = RaceDay.objects.get(id=race_day_id)
                    except RaceDay.DoesNotExist:
                        if race_day_id not in race_day_not_found:
                            self.stdout.write(self.style.WARNING(f'Race day not found: ID {race_day_id}'))
                            race_day_not_found.append(race_day_id)
                        error_count += 1
                        continue
                    
                    if dry_run:
                        self.stdout.write(
                            f'Would create result: {rider.full_name} - {race_day} - Position {position} - Points {points}'
                        )
                        created_count += 1
                    else:
                        try:
                            with transaction.atomic():
                                # Create or update race day result
                                result, created = RaceDayResult.objects.update_or_create(
                                    race_day=race_day,
                                    rider=rider,
                                    defaults={
                                        'position': position,
                                        'points_earned': points,
                                    }
                                )
                                
                                action = 'Created' if created else 'Updated'
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'{action}: {rider.full_name} - {race_day} - P{position} - {points} pts'
                                    )
                                )
                                created_count += 1
                                
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error creating result for {username} on {col}: {str(e)}')
                            )
                            error_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 70}'))
        self.stdout.write(self.style.SUCCESS(f'Import completed!'))
        self.stdout.write(self.style.SUCCESS(f'Results created/updated: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Skipped: {skipped_count}'))
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'Errors: {error_count}'))
        if rider_not_found:
            self.stdout.write(self.style.WARNING(f'Riders not found: {len(rider_not_found)}'))
        if race_day_not_found:
            self.stdout.write(self.style.WARNING(f'Race days not found (IDs): {", ".join(race_day_not_found)}'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 70}'))

