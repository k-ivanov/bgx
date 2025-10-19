from rest_framework import serializers
from .models import RaceDayResult, RaceResult, ChampionshipResult, ClubResult
from .calculations import get_points_for_position


class RaceDayResultSerializer(serializers.ModelSerializer):
    """Serializer for race day results"""
    rider_name = serializers.CharField(source='rider.full_name', read_only=True)
    race_day_info = serializers.SerializerMethodField()
    
    class Meta:
        model = RaceDayResult
        fields = ['id', 'race_day', 'race_day_info', 'rider', 'rider_name',
                  'position', 'time_taken', 'points_earned', 'penalties',
                  'dnf', 'dsq', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_race_day_info(self, obj):
        return {
            'day_number': obj.race_day.day_number,
            'type': obj.race_day.type,
            'date': obj.race_day.date
        }
    
    def validate(self, data):
        # Auto-calculate points based on position if not provided
        if 'points_earned' not in data or data['points_earned'] == 0:
            data['points_earned'] = get_points_for_position(data['position'])
        return data


class RaceResultSerializer(serializers.ModelSerializer):
    """Serializer for overall race results"""
    rider_name = serializers.CharField(source='rider.full_name', read_only=True)
    rider_club = serializers.CharField(source='rider.club.name', read_only=True, allow_null=True)
    race_name = serializers.CharField(source='race.name', read_only=True)
    
    class Meta:
        model = RaceResult
        fields = ['id', 'race', 'race_name', 'rider', 'rider_name', 'rider_club',
                  'category', 'overall_position', 'total_time', 'total_points',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'overall_position', 'total_time', 'total_points',
                            'created_at', 'updated_at']


class ChampionshipResultSerializer(serializers.ModelSerializer):
    """Serializer for championship standings"""
    rider_name = serializers.CharField(source='rider.full_name', read_only=True)
    rider_club = serializers.CharField(source='rider.club.name', read_only=True, allow_null=True)
    championship_name = serializers.CharField(source='championship.name', read_only=True)
    
    class Meta:
        model = ChampionshipResult
        fields = ['id', 'championship', 'championship_name', 'rider', 'rider_name',
                  'rider_club', 'category', 'total_points', 'races_participated',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'total_points', 'races_participated',
                            'created_at', 'updated_at']


class ClubResultSerializer(serializers.ModelSerializer):
    """Serializer for club standings"""
    club_name = serializers.CharField(source='club.name', read_only=True)
    championship_name = serializers.CharField(source='championship.name', read_only=True)
    
    class Meta:
        model = ClubResult
        fields = ['id', 'championship', 'championship_name', 'club', 'club_name',
                  'total_points', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_points', 'created_at', 'updated_at']

