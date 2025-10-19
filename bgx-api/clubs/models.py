from django.db import models
from django.conf import settings


class Club(models.Model):
    """Model representing a racing club"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='clubs/logos/', blank=True, null=True)
    founded_date = models.DateField(null=True, blank=True)
    
    # Contact information
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Bulgaria')
    
    # Admins who can manage this club
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='managed_clubs',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Club'
        verbose_name_plural = 'Clubs'
    
    def __str__(self):
        return self.name

