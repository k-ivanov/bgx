from django.contrib import admin
from .models import Rider


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user_email', 'club', 'is_licensed', 'license_expiry', 'created_at']
    list_filter = ['is_licensed', 'club', 'license_expiry']
    search_fields = ['first_name', 'last_name', 'user__email', 'license_number']
    raw_id_fields = ['user', 'club']
    readonly_fields = ['user_email', 'username']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'username', 'user_email')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'photo', 'phone')
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
    
    def user_email(self, obj):
        """Display user's email"""
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def username(self, obj):
        """Display username"""
        return obj.user.username if obj.user else '-'
    username.short_description = 'Username'
    username.admin_order_field = 'user__username'

