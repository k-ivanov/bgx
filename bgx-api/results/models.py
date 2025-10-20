from django.db import models


class RaceDayResult(models.Model):
    """Results for a single race day/stage"""
    race_day = models.ForeignKey(
        'races.RaceDay',
        on_delete=models.CASCADE,
        related_name='results'
    )
    rider = models.ForeignKey(
        'riders.Rider',
        on_delete=models.CASCADE,
        related_name='race_day_results'
    )
    
    position = models.IntegerField()
    time_taken = models.DurationField(null=True, blank=True, help_text="Time to complete the stage")
    points_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Penalties and disqualifications
    penalties = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Time penalties in seconds"
    )
    dnf = models.BooleanField(default=False, help_text="Did Not Finish")
    dsq = models.BooleanField(default=False, help_text="Disqualified")
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['race_day', 'position']
        verbose_name = 'Race Day Result'
        verbose_name_plural = 'Race Day Results'
        unique_together = ['race_day', 'rider']
    
    def __str__(self):
        return f"{self.rider.full_name} - {self.race_day} - P{self.position}"


class RaceResult(models.Model):
    """Overall results for an entire race"""
    race = models.ForeignKey(
        'races.Race',
        on_delete=models.CASCADE,
        related_name='overall_results'
    )
    rider = models.ForeignKey(
        'riders.Rider',
        on_delete=models.CASCADE,
        related_name='race_results'
    )
    category = models.CharField(max_length=20)
    
    overall_position = models.IntegerField()
    total_time = models.DurationField(null=True, blank=True)
    total_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['race', 'category', 'overall_position']
        verbose_name = 'Race Result'
        verbose_name_plural = 'Race Results'
        unique_together = ['race', 'rider']
    
    def __str__(self):
        return f"{self.rider.full_name} - {self.race.name} - P{self.overall_position}"


class ChampionshipResult(models.Model):
    """Overall championship standings"""
    championship = models.ForeignKey(
        'championships.Championship',
        on_delete=models.CASCADE,
        related_name='standings'
    )
    rider = models.ForeignKey(
        'riders.Rider',
        on_delete=models.CASCADE,
        related_name='championship_results'
    )
    category = models.CharField(max_length=20)
    
    total_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    races_participated = models.IntegerField(default=0)
    lowest_score_dropped = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Lowest race score dropped (if rider participated in all races of completed championship)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['championship', 'category', '-total_points']
        verbose_name = 'Championship Result'
        verbose_name_plural = 'Championship Results'
        unique_together = ['championship', 'rider', 'category']
    
    def __str__(self):
        return f"{self.rider.full_name} - {self.championship} - {self.total_points} pts"


class ClubResult(models.Model):
    """Club standings in a championship"""
    championship = models.ForeignKey(
        'championships.Championship',
        on_delete=models.CASCADE,
        related_name='club_standings'
    )
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='championship_results'
    )
    
    total_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['championship', '-total_points']
        verbose_name = 'Club Result'
        verbose_name_plural = 'Club Results'
        unique_together = ['championship', 'club']
    
    def __str__(self):
        return f"{self.club.name} - {self.championship} - {self.total_points} pts"

