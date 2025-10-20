import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from riders.models import Rider
from clubs.models import Club
import secrets
import string


User = get_user_model()


class Command(BaseCommand):
    help = 'Import riders from CSV file (creates users and rider profiles)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='input_data/user_racers/senior_50_processed.csv',
            help='Path to the CSV file (default: input_data/user_racers/expert_processed.csv)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually creating users and riders in the database'
        )
        parser.add_argument(
            '--password-length',
            type=int,
            default=12,
            help='Length of random password (default: 12)'
        )

    def generate_random_password(self, length=12):
        """Generate a secure random password."""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    def find_matching_club(self, club_name):
        """
        Find a club that matches the given club name.
        Checks if club_name is contained in any existing club's name.
        """
        if not club_name:
            return None
        
        # Try exact match first
        try:
            return Club.objects.get(name=club_name)
        except Club.DoesNotExist:
            pass
        
        # Try partial match - check if club_name is contained in any club
        clubs = Club.objects.all()
        for club in clubs:
            if club_name in club.name or club.name in club_name:
                return club
        
        return None

    def handle(self, *args, **options):
        csv_file = options['file']
        dry_run = options['dry_run']
        password_length = options['password_length']
        
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
        
        self.stdout.write(self.style.SUCCESS(f'Reading riders from: {file_path}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made to the database'))
        
        created_count = 0
        skipped_count = 0
        club_not_found_count = 0
        passwords = []  # Store username:password pairs for reporting
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Extract data from CSV
                username = row.get('username', '').strip()
                first_name = row.get('Име', '').strip()
                last_name = row.get('Фамилия', '').strip()
                license_number = row.get('Ст.№', '').strip()
                club_name = row.get('Отбор', '').strip()
                bike = row.get('Мотор', '').strip()
                
                if not username or not first_name or not last_name:
                    self.stdout.write(self.style.WARNING(f'Skipping row with missing data: {row}'))
                    skipped_count += 1
                    continue
                
                # Check if user already exists
                existing_user = User.objects.filter(username=username).first()
                if existing_user:
                    # Check if rider profile exists
                    if hasattr(existing_user, 'rider_profile'):
                        self.stdout.write(
                            self.style.WARNING(
                                f'User and rider profile already exist: {username} - SKIPPING'
                            )
                        )
                        skipped_count += 1
                        continue
                    else:
                        self.stdout.write(
                            self.style.NOTICE(
                                f'User exists but no rider profile: {username} - Will create profile only'
                            )
                        )
                
                # Find matching club
                club = self.find_matching_club(club_name)
                if not club and club_name:
                    self.stdout.write(self.style.WARNING(f'Club not found for: {club_name} (rider: {username})'))
                    club_not_found_count += 1
                
                if dry_run:
                    club_info = f" -> Club: {club.name}" if club else " -> Club: NOT FOUND"
                    action = "rider profile only" if existing_user else "user and rider"
                    self.stdout.write(
                        f'Would create {action}: {username} ({first_name} {last_name}){club_info}'
                    )
                    created_count += 1
                else:
                    # Generate random password (only if creating new user)
                    password = None if existing_user else self.generate_random_password(password_length)
                    
                    try:
                        with transaction.atomic():
                            # Create user if doesn't exist
                            if existing_user:
                                user = existing_user
                                # Update is_rider flag
                                user.is_rider = True
                                user.save()
                            else:
                                # Create new user
                                user = User.objects.create_user(
                                    username=username,
                                    password=password,
                                    first_name=first_name,
                                    last_name=last_name,
                                    is_rider=True
                                )
                            
                            # Prepare bike info
                            bike_info = {}
                            if bike:
                                bike_info = {'model': bike}
                            
                            # Create rider profile
                            rider = Rider.objects.create(
                                user=user,
                                first_name=first_name,
                                last_name=last_name,
                                license_number=license_number,
                                is_licensed=True,
                                club=club,
                                bike_info=bike_info
                            )
                            
                            # Only save password if we created a new user
                            if password:
                                passwords.append(f"{username}:{password}")
                            
                            club_info = f" (Club: {club.name})" if club else " (No club)"
                            action = "rider profile for existing user" if existing_user else "user and rider"
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Created {action}: {username} - {first_name} {last_name}{club_info}'
                                )
                            )
                            created_count += 1
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error creating rider for {username}: {str(e)}')
                        )
                        skipped_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 70}'))
        self.stdout.write(self.style.SUCCESS(f'Import completed!'))
        self.stdout.write(self.style.SUCCESS(f'Users/Riders created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Skipped (already exist or errors): {skipped_count}'))
        if club_not_found_count > 0:
            self.stdout.write(self.style.WARNING(f'Clubs not found: {club_not_found_count}'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 70}'))
        
        # Display passwords if users were created
        if passwords and not dry_run:
            self.stdout.write(self.style.WARNING(f'\n⚠️  IMPORTANT: Save these passwords securely!'))
            self.stdout.write(self.style.WARNING(f'{"=" * 70}'))
            for cred in passwords:
                self.stdout.write(cred)
            self.stdout.write(self.style.WARNING(f'{"=" * 70}'))
            
            # Optionally save to a file
            output_file = 'rider_credentials.txt'
            try:
                with open(output_file, 'w') as f:
                    f.write('# Rider Credentials - KEEP SECURE\n')
                    f.write('# Format: username:password\n\n')
                    for cred in passwords:
                        f.write(f'{cred}\n')
                self.stdout.write(
                    self.style.SUCCESS(f'\n✓ Credentials saved to: {output_file}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Could not save credentials to file: {str(e)}')
                )

