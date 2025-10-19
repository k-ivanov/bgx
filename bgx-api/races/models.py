from django.db import models


class Race(models.Model):
    """Model representing a race event"""
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Registration
    registration_open = models.BooleanField(default=True)
    registration_deadline = models.DateField(null=True, blank=True)
    max_participants = models.IntegerField(null=True, blank=True)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Relationships
    organizers = models.ManyToManyField(
        'clubs.Club',
        related_name='organized_races'
    )
    championships = models.ManyToManyField(
        'championships.Championship',
        related_name='races',
        blank=True
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Race'
        verbose_name_plural = 'Races'
    
    def __str__(self):
        return f"{self.name} ({self.start_date.year})"


class RaceDay(models.Model):
    """Model representing a single day/stage of a race"""
    
    TYPE_CHOICES = [
        ('prologue', 'Prologue (Qualification)'),
        ('navigation', 'Navigation'),
        ('endurocross', 'Endurocross'),
    ]
    
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='race_days'
    )
    day_number = models.IntegerField(help_text="Day order (1, 2, 3, etc.)")
    date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    specific_rules = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['race', 'day_number']
        verbose_name = 'Race Day'
        verbose_name_plural = 'Race Days'
        unique_together = ['race', 'day_number']
    
    def __str__(self):
        return f"{self.race.name} - Day {self.day_number} ({self.get_type_display()})"


class RaceParticipation(models.Model):
    """Model representing a rider's registration/participation in a race"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CATEGORY_CHOICES = [
        ('expert', 'Expert'),
        ('profi', 'Profi'),
        ('junior', 'Junior'),
        ('standard', 'Standard'),
        ('standard_junior', 'Standard Junior'),
        ('seniors_40', 'Seniors 40+'),
        ('seniors_50', 'Seniors 50+'),
        ('women', 'Women'),
    ]
    
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    rider = models.ForeignKey(
        'riders.Rider',
        on_delete=models.CASCADE,
        related_name='race_participations'
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bib_number = models.CharField(max_length=10, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['race', 'category', 'bib_number']
        verbose_name = 'Race Participation'
        verbose_name_plural = 'Race Participations'
        unique_together = ['race', 'rider']
    
    def __str__(self):
        return f"{self.rider.full_name} - {self.race.name} ({self.category})"

