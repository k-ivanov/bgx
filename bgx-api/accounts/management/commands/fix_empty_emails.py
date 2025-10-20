from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Fix users with empty emails by generating unique placeholder emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually updating users'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Find users with empty emails
        users_with_empty_email = User.objects.filter(email='')
        count = users_with_empty_email.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No users with empty emails found!'))
            return
        
        self.stdout.write(f'Found {count} users with empty emails')
        
        updated = 0
        for user in users_with_empty_email:
            # Generate a placeholder email based on username
            new_email = f"{user.username}@placeholder.bgx-navigation.local"
            
            self.stdout.write(f'  User: {user.username} -> {new_email}')
            
            if not dry_run:
                user.email = new_email
                user.save()
                updated += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 70}'))
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Would update {count} users'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated {updated} users'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 70}'))
        self.stdout.write(self.style.WARNING('\nNote: Users will need to update their emails to real addresses'))

