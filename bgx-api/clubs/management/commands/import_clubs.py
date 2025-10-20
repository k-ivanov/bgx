import csv
import os
from django.core.management.base import BaseCommand
from clubs.models import Club


class Command(BaseCommand):
    help = 'Import clubs from CSV file (input_data/teams.csv)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='input_data/teams.csv',
            help='Path to the CSV file (default: input_data/teams.csv)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually creating clubs in the database'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        dry_run = options['dry_run']
        
        # Build the full path
        # If running in Docker, input_data is mounted at /app/input_data
        # If running locally, navigate to project root
        if os.path.isabs(csv_file):
            file_path = csv_file
        elif os.path.exists(csv_file):
            # Direct relative path works
            file_path = csv_file
        else:
            # Try different base paths
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            
            # Try: /app/input_data/teams.csv (Docker)
            file_path = os.path.join('/app', csv_file)
            if not os.path.exists(file_path):
                # Try: bgx-api/../input_data/teams.csv (local)
                project_root = os.path.dirname(base_dir)
                file_path = os.path.join(project_root, csv_file)
            if not os.path.exists(file_path):
                # Try: bgx-api/input_data/teams.csv (local alternative)
                file_path = os.path.join(base_dir, csv_file)
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            self.stdout.write(self.style.ERROR(f'Searched in multiple locations. Please check the file path.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Reading clubs from: {file_path}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made to the database'))
        
        created_count = 0
        skipped_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # Skip header row
            next(reader)
            
            for row in reader:
                if len(row) < 2:
                    self.stdout.write(self.style.WARNING(f'Skipping invalid row: {row}'))
                    continue
                
                # Extract Cyrillic name and phonetical name
                cyrillic_name = row[0].strip()
                phonetical_name = row[1].strip()
                
                if not cyrillic_name:
                    self.stdout.write(self.style.WARNING(f'Skipping row with empty Cyrillic name'))
                    continue
                
                # Check if club already exists
                if Club.objects.filter(name=cyrillic_name).exists():
                    self.stdout.write(self.style.WARNING(f'Club already exists: {cyrillic_name}'))
                    skipped_count += 1
                    continue
                
                if dry_run:
                    self.stdout.write(f'Would create club: {cyrillic_name} ({phonetical_name})')
                    created_count += 1
                else:
                    # Create the club with Cyrillic name
                    club = Club.objects.create(
                        name=cyrillic_name,
                        description=f'Phonetical name: {phonetical_name}',
                        country='Bulgaria'
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created club: {club.name}'))
                    created_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 50}'))
        self.stdout.write(self.style.SUCCESS(f'Import completed!'))
        self.stdout.write(self.style.SUCCESS(f'Clubs created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Clubs skipped (already exist): {skipped_count}'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 50}'))

