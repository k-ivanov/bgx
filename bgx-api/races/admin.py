from django.contrib import admin
from django.utils.html import format_html
from .models import Race, RaceDay, RaceParticipation


class RaceDayInline(admin.TabularInline):
    """Inline view to display race days/stages"""
    model = RaceDay
    extra = 1
    fields = ['day_number', 'date', 'type', 'type_badge', 'description', 'specific_rules']
    readonly_fields = ['type_badge']
    ordering = ['day_number']
    classes = ['collapse']
    
    def type_badge(self, obj):
        """Display race day type with color coding"""
        if obj.type:
            colors = {
                'prologue': '#6f42c1',
                'navigation': '#0d6efd',
                'endurocross': '#dc3545'
            }
            type_display = obj.get_type_display()
            color = colors.get(obj.type, '#6c757d')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
                color,
                type_display
            )
        return '-'
    type_badge.short_description = 'Type Badge'


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'start_date', 'end_date', 'race_days_count', 'status', 'registration_open']
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
        ('Race Days Summary', {
            'fields': ('get_race_days_summary',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['get_race_days_summary']
    
    def race_days_count(self, obj):
        """Display the number of race days"""
        count = obj.race_days.count()
        if count == 0:
            return format_html('<span style="color: #dc3545;">0 days</span>')
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{} day{}</span>',
            count,
            's' if count > 1 else ''
        )
    race_days_count.short_description = 'Race Days'
    
    def get_race_days_summary(self, obj):
        """Display a summary of all race days"""
        race_days = obj.race_days.order_by('day_number')
        
        if not race_days.exists():
            return format_html('<p style="color: #dc3545;">⚠️ No race days configured yet. Add race days below.</p>')
        
        summary_html = '<div style="margin: 10px 0;">'
        summary_html += f'<p><strong>Total Race Days: {race_days.count()}</strong></p>'
        summary_html += '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">'
        summary_html += '''
            <thead>
                <tr style="background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 8px; text-align: center;">Day</th>
                    <th style="padding: 8px; text-align: left;">Date</th>
                    <th style="padding: 8px; text-align: left;">Type</th>
                    <th style="padding: 8px; text-align: left;">Description</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for day in race_days:
            type_colors = {
                'prologue': '#6f42c1',
                'navigation': '#0d6efd',
                'endurocross': '#dc3545'
            }
            color = type_colors.get(day.type, '#6c757d')
            
            summary_html += format_html(
                '''<tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 8px; text-align: center; font-weight: bold;">Day {}</td>
                    <td style="padding: 8px;">{}</td>
                    <td style="padding: 8px;">
                        <span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">
                            {}
                        </span>
                    </td>
                    <td style="padding: 8px;">{}</td>
                </tr>''',
                day.day_number,
                day.date,
                color,
                day.get_type_display(),
                day.description or '-'
            )
        
        summary_html += '</tbody></table></div>'
        
        return format_html(summary_html)
    get_race_days_summary.short_description = 'Race Days Overview'


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

