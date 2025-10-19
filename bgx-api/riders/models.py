from django.db import models
from django.conf import settings


class Rider(models.Model):
    """Model representing a rider/racer"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rider_profile'
    )
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='riders'
    )
    
    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    photo = models.ImageField(upload_to='riders/photos/', blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # License information
    is_licensed = models.BooleanField(default=False)
    license_number = models.CharField(max_length=50, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    
    # Equipment information (stored as JSON)
    bike_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Bike details: brand, model, year, etc."
    )
    gear_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Gear and equipment details"
    )
    
    # Emergency contact
    emergency_contact = models.JSONField(
        default=dict,
        blank=True,
        help_text="Emergency contact: name, phone, relationship"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Rider'
        verbose_name_plural = 'Riders'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

