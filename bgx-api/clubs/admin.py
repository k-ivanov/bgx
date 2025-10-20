from django.contrib import admin
from django.utils.html import format_html
from .models import Club
from riders.models import Rider


class RiderInline(admin.TabularInline):
    """Inline view to display riders in the club (read-only)"""
    model = Rider
    extra = 0
    fields = ['first_name', 'last_name', 'license_number', 'is_licensed', 'user_link']
    readonly_fields = ['first_name', 'last_name', 'license_number', 'is_licensed', 'user_link']
    can_delete = False
    classes = ['collapse']
    
    def has_add_permission(self, request, obj=None):
        """Disable adding riders from club view"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing riders from club view"""
        return False
    
    def user_link(self, obj):
        """Link to the user account"""
        if obj.user:
            return format_html(
                '<a href="/admin/accounts/user/{}/change/">{}</a>',
                obj.user.id,
                obj.user.username
            )
        return '-'
    user_link.short_description = 'Username'


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'contact_email', 'rider_count', 'founded_date', 'created_at']
    list_filter = ['country', 'city', 'founded_date']
    search_fields = ['name', 'city', 'contact_email']
    filter_horizontal = ['admins']
    inlines = [RiderInline]
    
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
        ('Statistics', {
            'fields': ('get_rider_list',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['get_rider_list']
    
    def rider_count(self, obj):
        """Display the number of riders in the club"""
        count = obj.riders.count()
        return format_html(
            '<a href="/admin/riders/rider/?club__id__exact={}">{} riders</a>',
            obj.id,
            count
        )
    rider_count.short_description = 'Riders'
    
    def get_rider_list(self, obj):
        """Display a formatted list of all riders in the club"""
        riders = obj.riders.select_related('user').order_by('last_name', 'first_name')
        
        if not riders.exists():
            return format_html('<p>No riders in this club yet.</p>')
        
        rider_html = '<ul style="margin: 0; padding-left: 20px;">'
        for rider in riders:
            rider_html += format_html(
                '<li><strong>{} {}</strong> (License: {}) - User: <a href="/admin/accounts/user/{}/change/">{}</a></li>',
                rider.first_name,
                rider.last_name,
                rider.license_number or 'N/A',
                rider.user.id,
                rider.user.username
            )
        rider_html += '</ul>'
        
        return format_html(rider_html)
    get_rider_list.short_description = 'Club Members'

