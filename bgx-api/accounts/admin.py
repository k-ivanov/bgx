from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 
                    'is_rider', 'is_club_admin', 'is_system_admin', 'is_staff']
    list_filter = ['is_rider', 'is_club_admin', 'is_system_admin', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Roles', {'fields': ('is_rider', 'is_club_admin', 'is_system_admin')}),
    )

