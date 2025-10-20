"""
Django management command to calculate/recalculate championship results

Usage:
    # Recalculate all championships
    python manage.py recalculate_results

    # Recalculate specific championship
    python manage.py recalculate_results --championship 1

    # Recalculate specific race
    python manage.py recalculate_results --race 5

    # Recalculate only completed championships
    python manage.py recalculate_results --completed-only

    # Dry run (show what would be done)
    python manage.py recalculate_results --dry-run
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from championships.models import Championship
from races.models import Race
from results.models import ChampionshipResult, RaceResult, ClubResult
from results.calculations import (
    calculate_race_results,
    calculate_championship_results,
    calculate_club_results,
    recalculate_all
)


class Command(BaseCommand):
    help = 'Calculate or recalculate championship results'

    def add_arguments(self, parser):
        parser.add_argument(
            '--championship',
            type=int,
            help='Recalculate specific championship by ID',
        )
        parser.add_argument(
            '--race',
            type=int,
            help='Recalculate specific race and related championships',
        )
        parser.add_argument(
            '--completed-only',
            action='store_true',
            help='Only recalculate completed championships',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        championship_id = options.get('championship')
        race_id = options.get('race')
        completed_only = options.get('completed_only')
        dry_run = options.get('dry_run')
        verbose = options.get('verbose')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
            self.stdout.write('')

        try:
            if race_id:
                self.recalculate_race(race_id, dry_run, verbose)
            elif championship_id:
                self.recalculate_championship(championship_id, dry_run, verbose)
            else:
                self.recalculate_all_championships(completed_only, dry_run, verbose)
                
            if not dry_run:
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('✓ Recalculation completed successfully'))
            else:
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('✓ Dry run completed - no changes made'))
                
        except Exception as e:
            raise CommandError(f'Error during recalculation: {str(e)}')

    def recalculate_race(self, race_id, dry_run, verbose):
        """Recalculate a specific race and related championships"""
        try:
            race = Race.objects.get(id=race_id)
        except Race.DoesNotExist:
            raise CommandError(f'Race with ID {race_id} does not exist')

        self.stdout.write(self.style.MIGRATE_HEADING(f'Recalculating Race: {race.name}'))
        self.stdout.write('')

        if not dry_run:
            with transaction.atomic():
                # Recalculate race results
                race_results = calculate_race_results(race)
                self.stdout.write(f'  ✓ Calculated {race_results.count()} race results')

                # Recalculate related championships
                championships = race.championships.all()
                self.stdout.write(f'  ✓ Updating {championships.count()} related championship(s)')
                
                for champ in championships:
                    champ_results = calculate_championship_results(champ)
                    club_results = calculate_club_results(champ)
                    
                    if verbose:
                        self.stdout.write(f'    • {champ.name}: {champ_results.count()} rider results, {club_results.count()} club results')
        else:
            race_results = RaceResult.objects.filter(race=race)
            championships = race.championships.all()
            
            self.stdout.write(f'  Would calculate {race_results.count()} race results')
            self.stdout.write(f'  Would update {championships.count()} related championship(s)')
            
            for champ in championships:
                champ_results = ChampionshipResult.objects.filter(championship=champ)
                club_results = ClubResult.objects.filter(championship=champ)
                self.stdout.write(f'    • {champ.name}: {champ_results.count()} rider results, {club_results.count()} club results')

    def recalculate_championship(self, championship_id, dry_run, verbose):
        """Recalculate a specific championship"""
        try:
            championship = Championship.objects.get(id=championship_id)
        except Championship.DoesNotExist:
            raise CommandError(f'Championship with ID {championship_id} does not exist')

        self.stdout.write(self.style.MIGRATE_HEADING(f'Recalculating Championship: {championship.name} ({championship.year})'))
        self.stdout.write(f'  Status: {championship.status.upper()}')
        
        races = championship.races.all()
        self.stdout.write(f'  Races: {races.count()}')
        self.stdout.write('')

        if not dry_run:
            with transaction.atomic():
                # Recalculate all races first
                for race in races:
                    race_results = calculate_race_results(race)
                    if verbose:
                        self.stdout.write(f'  ✓ {race.name}: {race_results.count()} results')

                # Then recalculate championship standings
                champ_results = calculate_championship_results(championship)
                club_results = calculate_club_results(championship)

                self.stdout.write('')
                self.stdout.write(f'  ✓ Championship results: {champ_results.count()} riders')
                self.stdout.write(f'  ✓ Club results: {club_results.count()} clubs')

                # Show drop-lowest-score info
                dropped_scores = champ_results.filter(lowest_score_dropped__gt=0)
                if dropped_scores.exists():
                    self.stdout.write('')
                    self.stdout.write(self.style.WARNING(f'  ℹ️  {dropped_scores.count()} rider(s) had lowest score dropped (participated in all races)'))
                    
                    if verbose:
                        for result in dropped_scores:
                            self.stdout.write(f'      • {result.rider.full_name} ({result.category}): dropped {result.lowest_score_dropped} pts')
        else:
            champ_results = ChampionshipResult.objects.filter(championship=championship)
            club_results = ClubResult.objects.filter(championship=championship)
            
            self.stdout.write(f'  Would calculate {races.count()} race results')
            self.stdout.write(f'  Would update {champ_results.count()} rider results')
            self.stdout.write(f'  Would update {club_results.count()} club results')

    def recalculate_all_championships(self, completed_only, dry_run, verbose):
        """Recalculate all championships"""
        championships = Championship.objects.all()
        
        if completed_only:
            championships = championships.filter(status='completed')
            self.stdout.write(self.style.MIGRATE_HEADING('Recalculating All COMPLETED Championships'))
        else:
            self.stdout.write(self.style.MIGRATE_HEADING('Recalculating All Championships'))

        self.stdout.write(f'  Found {championships.count()} championship(s)')
        self.stdout.write('')

        if championships.count() == 0:
            self.stdout.write(self.style.WARNING('  No championships to recalculate'))
            return

        total_riders = 0
        total_clubs = 0
        total_dropped = 0

        for i, championship in enumerate(championships, 1):
            self.stdout.write(f'  [{i}/{championships.count()}] {championship.name} ({championship.year}) - {championship.status}')
            
            races = championship.races.all()
            
            if not dry_run:
                with transaction.atomic():
                    # Recalculate all races in this championship
                    for race in races:
                        calculate_race_results(race)
                    
                    # Recalculate championship standings
                    champ_results = calculate_championship_results(championship)
                    club_results = calculate_club_results(championship)
                    
                    dropped_scores = champ_results.filter(lowest_score_dropped__gt=0).count()
                    
                    total_riders += champ_results.count()
                    total_clubs += club_results.count()
                    total_dropped += dropped_scores
                    
                    if verbose:
                        self.stdout.write(f'      • {races.count()} races, {champ_results.count()} riders, {club_results.count()} clubs')
                        if dropped_scores > 0:
                            self.stdout.write(self.style.WARNING(f'      • {dropped_scores} rider(s) had lowest score dropped'))
            else:
                champ_results = ChampionshipResult.objects.filter(championship=championship)
                club_results = ClubResult.objects.filter(championship=championship)
                
                self.stdout.write(f'      Would process {races.count()} races, {champ_results.count()} riders, {club_results.count()} clubs')

        if not dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f'  Total: {total_riders} rider results, {total_clubs} club results'))
            if total_dropped > 0:
                self.stdout.write(self.style.WARNING(f'  Total: {total_dropped} lowest scores dropped'))

