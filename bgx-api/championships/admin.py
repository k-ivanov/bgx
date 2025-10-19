from django.contrib import admin
from .models import Championship


@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['year', 'status']
    search_fields = ['name', 'year']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'year', 'description', 'logo')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Additional Information', {
            'fields': ('sponsor_info',)
        }),
    )

