from django.contrib.auth.models import AbstractUser
from django.db import models
import secrets


class User(AbstractUser):
    """
    Custom User model with role-based flags and activation
    """
    # Role flags
    is_rider = models.BooleanField(default=False, help_text="User has a rider profile")
    is_club_admin = models.BooleanField(default=False, help_text="User can manage one or more clubs")
    is_system_admin = models.BooleanField(default=False, help_text="User is a system administrator")
    
    # Activation
    activation_code = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Activation code for email verification"
    )
    is_activated = models.BooleanField(
        default=False,
        help_text="Whether the user has activated their account via email"
    )
    
    # Email field with unique constraint
    email = models.EmailField(
        'email address',
        unique=True,
        blank=True,
        help_text="Email address for the user."
    )
    
    def generate_activation_code(self):
        """Generate a random activation code"""
        self.activation_code = secrets.token_urlsafe(32)
        return self.activation_code
    
    def activate(self):
        """Activate the user account"""
        self.is_activated = True
        self.activation_code = None
        self.save()
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

