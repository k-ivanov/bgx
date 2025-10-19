"""
Points calculation utilities for race results
"""
from datetime import timedelta
from decimal import Decimal
from .models import RaceDayResult, RaceResult, ChampionshipResult, ClubResult


# Default point schema (position -> points)
DEFAULT_POINT_SCHEMA = {
    1: 25, 2: 20, 3: 16, 4: 13, 5: 11,
    6: 10, 7: 9, 8: 8, 9: 7, 10: 6,
    11: 5, 12: 4, 13: 3, 14: 2, 15: 1
}


def get_points_for_position(position, point_schema=None):
    """
    Get points for a given position based on the point schema
    """
    if point_schema is None:
        point_schema = DEFAULT_POINT_SCHEMA
    
    return Decimal(point_schema.get(position, 0))


def calculate_race_results(race):
    """
    Calculate overall race results from race day results
    Aggregates all race days for each rider
    """
    from races.models import RaceParticipation
    
    # Get all participations for this race
    participations = RaceParticipation.objects.filter(
        race=race,
        status='confirmed'
    ).select_related('rider')
    
    for participation in participations:
        rider = participation.rider
        category = participation.category
        
        # Get all race day results for this rider in this race
        day_results = RaceDayResult.objects.filter(
            race_day__race=race,
            rider=rider
        )
        
        # Skip if no results yet
        if not day_results.exists():
            continue
        
        # Check for DNF or DSQ
        has_dnf = day_results.filter(dnf=True).exists()
        has_dsq = day_results.filter(dsq=True).exists()
        
        if has_dnf or has_dsq:
            # Don't create/update race result for DNF/DSQ
            continue
        
        # Calculate total points and time
        total_points = sum(result.points_earned for result in day_results)
        
        # Calculate total time (if all results have time)
        total_time = None
        if all(result.time_taken for result in day_results):
            total_time = sum(
                (result.time_taken for result in day_results),
                timedelta()
            )
            # Add penalties
            total_penalties = sum(result.penalties for result in day_results)
            if total_penalties:
                total_time += timedelta(seconds=float(total_penalties))
        
        # Create or update race result
        race_result, created = RaceResult.objects.update_or_create(
            race=race,
            rider=rider,
            defaults={
                'category': category,
                'total_points': total_points,
                'total_time': total_time,
                'overall_position': 0  # Will be calculated after all results
            }
        )
    
    # Calculate positions by category
    categories = RaceResult.objects.filter(race=race).values_list('category', flat=True).distinct()
    
    for category in categories:
        category_results = RaceResult.objects.filter(
            race=race,
            category=category
        ).order_by('-total_points', 'total_time')
        
        for position, result in enumerate(category_results, start=1):
            result.overall_position = position
            result.save()
    
    return RaceResult.objects.filter(race=race)


def calculate_championship_results(championship):
    """
    Calculate championship standings from race results
    """
    from riders.models import Rider
    
    # Get all races in this championship
    races = championship.races.all()
    
    if not races.exists():
        return ChampionshipResult.objects.none()
    
    # Get all riders who participated in any race
    rider_ids = set()
    for race in races:
        race_rider_ids = RaceResult.objects.filter(
            race=race
        ).values_list('rider_id', flat=True)
        rider_ids.update(race_rider_ids)
    
    riders = Rider.objects.filter(id__in=rider_ids)
    
    for rider in riders:
        # Get all race results for this rider in this championship
        race_results = RaceResult.objects.filter(
            race__in=races,
            rider=rider
        )
        
        if not race_results.exists():
            continue
        
        # Group by category (a rider might compete in different categories)
        categories = race_results.values_list('category', flat=True).distinct()
        
        for category in categories:
            category_results = race_results.filter(category=category)
            
            total_points = sum(result.total_points for result in category_results)
            races_participated = category_results.count()
            
            ChampionshipResult.objects.update_or_create(
                championship=championship,
                rider=rider,
                category=category,
                defaults={
                    'total_points': total_points,
                    'races_participated': races_participated
                }
            )
    
    return ChampionshipResult.objects.filter(championship=championship)


def calculate_club_results(championship):
    """
    Calculate club standings in a championship
    Sum of all riders' points from that club
    """
    from clubs.models import Club
    
    # Get all championship results
    championship_results = ChampionshipResult.objects.filter(
        championship=championship
    ).select_related('rider__club')
    
    # Group by club
    club_points = {}
    for result in championship_results:
        if result.rider.club:
            club_id = result.rider.club.id
            if club_id not in club_points:
                club_points[club_id] = Decimal(0)
            club_points[club_id] += result.total_points
    
    # Create or update club results
    for club_id, total_points in club_points.items():
        club = Club.objects.get(id=club_id)
        ClubResult.objects.update_or_create(
            championship=championship,
            club=club,
            defaults={
                'total_points': total_points
            }
        )
    
    return ClubResult.objects.filter(championship=championship)


def recalculate_all(championship=None, race=None):
    """
    Recalculate all results
    If championship is provided, recalculate that championship
    If race is provided, recalculate that race and related championships
    """
    if race:
        # Recalculate this race
        calculate_race_results(race)
        
        # Recalculate all championships this race belongs to
        for champ in race.championships.all():
            calculate_championship_results(champ)
            calculate_club_results(champ)
    
    elif championship:
        # Recalculate all races in this championship first
        for race in championship.races.all():
            calculate_race_results(race)
        
        # Then recalculate championship standings
        calculate_championship_results(championship)
        calculate_club_results(championship)

