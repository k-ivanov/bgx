from rest_framework import serializers
from .models import Championship


class ChampionshipListSerializer(serializers.ModelSerializer):
    """Minimal serializer for championship lists"""
    race_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Championship
        fields = ['id', 'name', 'year', 'logo', 'start_date', 'end_date', 
                  'status', 'race_count']
    
    def get_race_count(self, obj):
        return obj.races.count()


class ChampionshipSerializer(serializers.ModelSerializer):
    """Standard championship serializer"""
    race_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Championship
        fields = ['id', 'name', 'year', 'description', 'logo', 'start_date', 
                  'end_date', 'sponsor_info', 'status', 'race_count',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_race_count(self, obj):
        return obj.races.count()


class ChampionshipDetailSerializer(serializers.ModelSerializer):
    """Detailed championship serializer with relationships"""
    races = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Championship
        fields = ['id', 'name', 'year', 'description', 'logo', 'start_date', 
                  'end_date', 'sponsor_info', 'status', 'races', 'participant_count',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_races(self, obj):
        from races.serializers import RaceListSerializer
        return RaceListSerializer(obj.races.all(), many=True).data
    
    def get_participant_count(self, obj):
        # Count unique riders across all races in this championship
        from riders.models import Rider
        rider_ids = set()
        for race in obj.races.all():
            race_rider_ids = race.participations.filter(
                status='confirmed'
            ).values_list('rider_id', flat=True)
            rider_ids.update(race_rider_ids)
        return len(rider_ids)


class ChampionshipWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating championships"""
    
    class Meta:
        model = Championship
        fields = ['name', 'year', 'description', 'logo', 'start_date', 
                  'end_date', 'sponsor_info', 'status']
    
    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("End date must be after start date.")
        return data

