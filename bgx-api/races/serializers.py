from rest_framework import serializers
from .models import Race, RaceDay, RaceParticipation
from clubs.serializers import ClubListSerializer
from riders.serializers import RiderListSerializer


class RaceListSerializer(serializers.ModelSerializer):
    """Minimal serializer for race lists"""
    organizer_names = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Race
        fields = ['id', 'name', 'location', 'start_date', 'end_date', 
                  'status', 'organizer_names', 'participant_count']
    
    def get_organizer_names(self, obj):
        return [organizer.name for organizer in obj.organizers.all()]
    
    def get_participant_count(self, obj):
        return obj.participations.filter(status='confirmed').count()


class RaceDaySerializer(serializers.ModelSerializer):
    """Serializer for race days"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = RaceDay
        fields = ['id', 'race', 'day_number', 'date', 'type', 'type_display', 
                  'description', 'specific_rules', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RaceParticipationSerializer(serializers.ModelSerializer):
    """Serializer for race participations"""
    rider_name = serializers.CharField(source='rider.full_name', read_only=True)
    race_name = serializers.CharField(source='race.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = RaceParticipation
        fields = ['id', 'race', 'race_name', 'rider', 'rider_name', 'category', 
                  'category_display', 'status', 'status_display', 'bib_number', 
                  'registration_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'registration_date', 'created_at', 'updated_at']


class RaceSerializer(serializers.ModelSerializer):
    """Standard race serializer"""
    organizers_details = ClubListSerializer(source='organizers', many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    day_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Race
        fields = ['id', 'name', 'description', 'location', 'start_date', 'end_date',
                  'registration_open', 'registration_deadline', 'max_participants', 
                  'entry_fee', 'organizers_details', 'status', 'participant_count',
                  'day_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_participant_count(self, obj):
        return obj.participations.filter(status='confirmed').count()
    
    def get_day_count(self, obj):
        return obj.race_days.count()


class RaceDetailSerializer(serializers.ModelSerializer):
    """Detailed race serializer with all relationships"""
    organizers = ClubListSerializer(many=True, read_only=True)
    championships_details = serializers.SerializerMethodField()
    race_days = RaceDaySerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Race
        fields = ['id', 'name', 'description', 'location', 'start_date', 'end_date',
                  'registration_open', 'registration_deadline', 'max_participants', 
                  'entry_fee', 'organizers', 'championships_details', 'race_days',
                  'status', 'participant_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_championships_details(self, obj):
        from championships.serializers import ChampionshipListSerializer
        return ChampionshipListSerializer(obj.championships.all(), many=True).data
    
    def get_participant_count(self, obj):
        return obj.participations.filter(status='confirmed').count()


class RaceWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating races"""
    organizer_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    championship_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Race
        fields = ['name', 'description', 'location', 'start_date', 'end_date',
                  'registration_open', 'registration_deadline', 'max_participants', 
                  'entry_fee', 'organizer_ids', 'championship_ids', 'status']
    
    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("End date must be after start date.")
        return data
    
    def create(self, validated_data):
        organizer_ids = validated_data.pop('organizer_ids')
        championship_ids = validated_data.pop('championship_ids', [])
        
        race = Race.objects.create(**validated_data)
        
        from clubs.models import Club
        race.organizers.set(Club.objects.filter(id__in=organizer_ids))
        
        if championship_ids:
            from championships.models import Championship
            race.championships.set(Championship.objects.filter(id__in=championship_ids))
        
        return race
    
    def update(self, instance, validated_data):
        organizer_ids = validated_data.pop('organizer_ids', None)
        championship_ids = validated_data.pop('championship_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if organizer_ids is not None:
            from clubs.models import Club
            instance.organizers.set(Club.objects.filter(id__in=organizer_ids))
        
        if championship_ids is not None:
            from championships.models import Championship
            instance.championships.set(Championship.objects.filter(id__in=championship_ids))
        
        return instance


class RaceSignupSerializer(serializers.Serializer):
    """Serializer for rider signup to a race"""
    category = serializers.ChoiceField(choices=RaceParticipation.CATEGORY_CHOICES)

