"""
Management command to import race results from CSV files
"""
import csv
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from races.models import Race, RaceDay
from riders.models import Rider
from results.models import RaceDayResult
from results.calculations import recalculate_all


class Command(BaseCommand):
    help = 'Import race results from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--race-day-id',
            type=int,
            required=True,
            help='ID of the race day to import results for'
        )
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to the CSV file'
        )
        parser.add_argument(
            '--match-by-name',
            action='store_true',
            help='Match riders by name if bib number not found'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without saving to database'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        race_day_id = options['race_day_id']
        file_path = options['file']
        match_by_name = options['match_by_name']
        dry_run = options['dry_run']

        # Get the race day
        try:
            race_day = RaceDay.objects.select_related('race').get(id=race_day_id)
        except RaceDay.DoesNotExist:
            raise CommandError(f'Race day with ID {race_day_id} does not exist')

        self.stdout.write(f'Importing results for: {race_day}')
        self.stdout.write(f'From file: {file_path}')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))

        # Read CSV file
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                imported = 0
                skipped = 0
                errors = []

                for row in reader:
                    try:
                        race_number = row.get('RaceNumber', '').strip()
                        first_name = row.get('FirstName', '').strip()
                        last_name = row.get('LastName', '').strip()
                        position = int(row.get('Position', 0))
                        points = Decimal(row.get('Points', 0))

                        # Try to find rider by bib number first
                        rider = None
                        
                        if race_number:
                            # Find rider through race participation
                            participation = race_day.race.participations.filter(
                                bib_number=race_number,
                                status='confirmed'
                            ).first()
                            
                            if participation:
                                rider = participation.rider

                        # If not found and match_by_name is enabled, try to match by name
                        if not rider and match_by_name and first_name and last_name:
                            rider = Rider.objects.filter(
                                first_name__iexact=first_name,
                                last_name__iexact=last_name
                            ).first()

                        if not rider:
                            errors.append(
                                f"Row {position}: Could not find rider - "
                                f"{first_name} {last_name} (#{race_number})"
                            )
                            skipped += 1
                            continue

                        # Create or update result
                        if not dry_run:
                            result, created = RaceDayResult.objects.update_or_create(
                                race_day=race_day,
                                rider=rider,
                                defaults={
                                    'position': position,
                                    'points_earned': points,
                                    'dnf': False,
                                    'dsq': False,
                                }
                            )
                            
                            action = 'Created' if created else 'Updated'
                            self.stdout.write(
                                f'{action} result: {rider.full_name} - P{position} ({points} pts)'
                            )
                        else:
                            self.stdout.write(
                                f'Would create/update: {rider.full_name} - P{position} ({points} pts)'
                            )

                        imported += 1

                    except Exception as e:
                        errors.append(f"Error processing row: {row}. Error: {str(e)}")
                        skipped += 1

        except FileNotFoundError:
            raise CommandError(f'File not found: {file_path}')
        except Exception as e:
            raise CommandError(f'Error reading file: {str(e)}')

        # Print summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Imported: {imported}'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped}'))
        
        if errors:
            self.stdout.write('\n' + self.style.ERROR('Errors:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))

        # Recalculate results
        if not dry_run and imported > 0:
            self.stdout.write('\nRecalculating race and championship results...')
            recalculate_all(race=race_day.race)
            self.stdout.write(self.style.SUCCESS('Recalculation complete!'))

        if dry_run:
            self.stdout.write('\n' + self.style.WARNING('DRY RUN COMPLETE - No changes were saved'))
            # Rollback transaction in dry run
            transaction.set_rollback(True)

