from django.contrib import admin
from django.utils.html import format_html
from .models import Championship
from races.models import Race


class RaceInline(admin.TabularInline):
    """Inline view to display races in the championship"""
    model = Race.championships.through
    extra = 0
    verbose_name = 'Race'
    verbose_name_plural = 'Races in Championship'
    classes = ['collapse']
    
    fields = ['race_link', 'race_location', 'race_start_date', 'race_end_date', 'race_status', 'race_registration']
    readonly_fields = ['race_link', 'race_location', 'race_start_date', 'race_end_date', 'race_status', 'race_registration']
    can_delete = True
    
    def race_link(self, obj):
        """Link to the race"""
        if obj.race:
            return format_html(
                '<a href="/admin/races/race/{}/change/"><strong>{}</strong></a>',
                obj.race.id,
                obj.race.name
            )
        return '-'
    race_link.short_description = 'Race Name'
    
    def race_location(self, obj):
        return obj.race.location if obj.race else '-'
    race_location.short_description = 'Location'
    
    def race_start_date(self, obj):
        return obj.race.start_date if obj.race else '-'
    race_start_date.short_description = 'Start Date'
    
    def race_end_date(self, obj):
        return obj.race.end_date if obj.race else '-'
    race_end_date.short_description = 'End Date'
    
    def race_status(self, obj):
        if obj.race:
            status = obj.race.status
            colors = {
                'upcoming': '#007bff',
                'ongoing': '#28a745',
                'completed': '#6c757d',
                'cancelled': '#dc3545'
            }
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                colors.get(status, '#000'),
                status.upper()
            )
        return '-'
    race_status.short_description = 'Status'
    
    def race_registration(self, obj):
        if obj.race:
            if obj.race.registration_open:
                return format_html('<span style="color: green;">✓ Open</span>')
            else:
                return format_html('<span style="color: red;">✗ Closed</span>')
        return '-'
    race_registration.short_description = 'Registration'
    
    def has_add_permission(self, request, obj=None):
        """You can still add races via the widget"""
        return True


@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'start_date', 'end_date', 'status', 'race_count', 'created_at']
    list_filter = ['year', 'status']
    search_fields = ['name', 'year']
    inlines = [RaceInline]
    
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
        ('Statistics', {
            'fields': ('get_race_summary',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['get_race_summary']
    
    def race_count(self, obj):
        """Display the number of races in the championship"""
        count = obj.races.count()
        return format_html(
            '<a href="/admin/races/race/?championships__id__exact={}">{} races</a>',
            obj.id,
            count
        )
    race_count.short_description = 'Races'
    
    def get_race_summary(self, obj):
        """Display a summary of all races in the championship"""
        races = obj.races.order_by('start_date')
        
        if not races.exists():
            return format_html('<p>No races in this championship yet.</p>')
        
        race_html = '<div style="margin: 10px 0;">'
        race_html += f'<p><strong>Total Races: {races.count()}</strong></p>'
        race_html += '<table style="width: 100%; border-collapse: collapse;">'
        race_html += '''
            <thead>
                <tr style="background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 8px; text-align: left;">Race Name</th>
                    <th style="padding: 8px; text-align: left;">Location</th>
                    <th style="padding: 8px; text-align: left;">Date</th>
                    <th style="padding: 8px; text-align: center;">Status</th>
                    <th style="padding: 8px; text-align: center;">Registration</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for race in races:
            status_colors = {
                'upcoming': '#007bff',
                'ongoing': '#28a745',
                'completed': '#6c757d',
                'cancelled': '#dc3545'
            }
            status_color = status_colors.get(race.status, '#000')
            reg_status = '✓ Open' if race.registration_open else '✗ Closed'
            reg_color = 'green' if race.registration_open else 'red'
            
            race_html += format_html(
                '''<tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 8px;"><a href="/admin/races/race/{}/change/">{}</a></td>
                    <td style="padding: 8px;">{}</td>
                    <td style="padding: 8px;">{} to {}</td>
                    <td style="padding: 8px; text-align: center; color: {}; font-weight: bold;">{}</td>
                    <td style="padding: 8px; text-align: center; color: {};">{}</td>
                </tr>''',
                race.id,
                race.name,
                race.location,
                race.start_date,
                race.end_date,
                status_color,
                race.status.upper(),
                reg_color,
                reg_status
            )
        
        race_html += '</tbody></table></div>'
        
        return format_html(race_html)
    get_race_summary.short_description = 'Race Summary'

