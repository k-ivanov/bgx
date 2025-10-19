from django.contrib import admin
from .models import Rider


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'club', 'is_licensed', 'license_expiry', 'created_at']
    list_filter = ['is_licensed', 'club', 'license_expiry']
    search_fields = ['first_name', 'last_name', 'email', 'license_number']
    raw_id_fields = ['user', 'club']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'photo', 'email', 'phone')
        }),
        ('Club', {
            'fields': ('club',)
        }),
        ('License Information', {
            'fields': ('is_licensed', 'license_number', 'license_expiry')
        }),
        ('Equipment', {
            'fields': ('bike_info', 'gear_info'),
            'classes': ('collapse',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact',),
            'classes': ('collapse',)
        }),
    )

