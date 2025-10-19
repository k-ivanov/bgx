from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based flags
    """
    is_rider = models.BooleanField(default=False, help_text="User has a rider profile")
    is_club_admin = models.BooleanField(default=False, help_text="User can manage one or more clubs")
    is_system_admin = models.BooleanField(default=False, help_text="User is a system administrator")
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

