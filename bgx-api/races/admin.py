from django.contrib import admin
from .models import Race, RaceDay, RaceParticipation


class RaceDayInline(admin.TabularInline):
    model = RaceDay
    extra = 1
    fields = ['day_number', 'date', 'type', 'description']


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'start_date', 'end_date', 'status', 'registration_open']
    list_filter = ['status', 'registration_open', 'start_date']
    search_fields = ['name', 'location']
    filter_horizontal = ['organizers', 'championships']
    inlines = [RaceDayInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'location')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Registration', {
            'fields': ('registration_open', 'registration_deadline', 'max_participants', 'entry_fee')
        }),
        ('Relationships', {
            'fields': ('organizers', 'championships')
        }),
    )


@admin.register(RaceDay)
class RaceDayAdmin(admin.ModelAdmin):
    list_display = ['race', 'day_number', 'date', 'type']
    list_filter = ['type', 'date']
    search_fields = ['race__name']
    raw_id_fields = ['race']


@admin.register(RaceParticipation)
class RaceParticipationAdmin(admin.ModelAdmin):
    list_display = ['rider', 'race', 'category', 'status', 'bib_number', 'registration_date']
    list_filter = ['status', 'category', 'registration_date']
    search_fields = ['rider__first_name', 'rider__last_name', 'race__name', 'bib_number']
    raw_id_fields = ['race', 'rider']

