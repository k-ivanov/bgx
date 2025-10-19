from django.db import models


class Championship(models.Model):
    """Model representing a racing championship/series"""
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=200)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='championships/logos/', blank=True, null=True)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    sponsor_info = models.TextField(blank=True, help_text="Sponsor information and details")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', 'name']
        verbose_name = 'Championship'
        verbose_name_plural = 'Championships'
        unique_together = ['name', 'year']
    
    def __str__(self):
        return f"{self.name} {self.year}"

