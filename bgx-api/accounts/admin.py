from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 
                    'is_activated_badge', 'is_rider', 'is_club_admin', 'is_system_admin', 'is_staff']
    list_filter = ['is_activated', 'is_rider', 'is_club_admin', 'is_system_admin', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Roles', {'fields': ('is_rider', 'is_club_admin', 'is_system_admin')}),
        ('Activation', {'fields': ('is_activated', 'activation_code')}),
    )
    
    readonly_fields = ['activation_code']
    
    def is_activated_badge(self, obj):
        """Display activation status with a badge"""
        if obj.is_activated:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activated</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚠ Pending</span>'
            )
    is_activated_badge.short_description = 'Activation Status'

