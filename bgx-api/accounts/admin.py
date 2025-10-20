from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 
                    'is_claimed_badge', 'is_activated_badge', 'is_rider', 'is_club_admin', 'is_system_admin', 'is_staff']
    list_filter = ['is_claimed', 'is_activated', 'is_rider', 'is_club_admin', 'is_system_admin', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Roles', {'fields': ('is_rider', 'is_club_admin', 'is_system_admin')}),
        ('Activation', {'fields': ('is_claimed', 'is_activated', 'activation_code')}),
    )
    
    readonly_fields = ['activation_code']
    
    def is_claimed_badge(self, obj):
        """Display claimed status with a badge"""
        if obj.is_claimed:
            return format_html(
                '<span style="color: blue; font-weight: bold;">✓ Claimed</span>'
            )
        else:
            return format_html(
                '<span style="color: gray; font-weight: bold;">○ Unclaimed</span>'
            )
    is_claimed_badge.short_description = 'Claimed'
    
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

