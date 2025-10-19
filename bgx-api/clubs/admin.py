from django.contrib import admin
from .models import Club


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'contact_email', 'founded_date', 'created_at']
    list_filter = ['country', 'city', 'founded_date']
    search_fields = ['name', 'city', 'contact_email']
    filter_horizontal = ['admins']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'logo', 'founded_date')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Administration', {
            'fields': ('admins',)
        }),
    )

