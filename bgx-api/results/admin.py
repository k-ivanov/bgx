from django.contrib import admin
from .models import RaceDayResult, RaceResult, ChampionshipResult, ClubResult


@admin.register(RaceDayResult)
class RaceDayResultAdmin(admin.ModelAdmin):
    list_display = ['rider', 'race_day', 'position', 'time_taken', 'points_earned', 'dnf', 'dsq']
    list_filter = ['race_day__race', 'race_day__type', 'dnf', 'dsq']
    search_fields = ['rider__first_name', 'rider__last_name', 'race_day__race__name']
    raw_id_fields = ['race_day', 'rider']


@admin.register(RaceResult)
class RaceResultAdmin(admin.ModelAdmin):
    list_display = ['rider', 'race', 'category', 'overall_position', 'total_points', 'total_time']
    list_filter = ['race', 'category']
    search_fields = ['rider__first_name', 'rider__last_name', 'race__name']
    raw_id_fields = ['race', 'rider']
    readonly_fields = ['overall_position', 'total_time', 'total_points']


@admin.register(ChampionshipResult)
class ChampionshipResultAdmin(admin.ModelAdmin):
    list_display = ['rider', 'championship', 'category', 'total_points', 'races_participated']
    list_filter = ['championship', 'category']
    search_fields = ['rider__first_name', 'rider__last_name', 'championship__name']
    raw_id_fields = ['championship', 'rider']
    readonly_fields = ['total_points', 'races_participated']


@admin.register(ClubResult)
class ClubResultAdmin(admin.ModelAdmin):
    list_display = ['club', 'championship', 'total_points']
    list_filter = ['championship']
    search_fields = ['club__name', 'championship__name']
    raw_id_fields = ['championship', 'club']
    readonly_fields = ['total_points']

