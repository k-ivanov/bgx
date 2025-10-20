from rest_framework import serializers
from .models import Rider
from clubs.serializers import ClubListSerializer


class RiderListSerializer(serializers.ModelSerializer):
    """Minimal serializer for rider lists"""
    club_name = serializers.CharField(source='club.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Rider
        fields = ['id', 'full_name', 'first_name', 'last_name', 'photo', 
                  'club_name', 'is_licensed']


class RiderSerializer(serializers.ModelSerializer):
    """Standard rider serializer"""
    club_name = serializers.CharField(source='club.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Rider
        fields = ['id', 'user', 'username', 'full_name', 'first_name', 'last_name',
                  'date_of_birth', 'photo', 'email', 'phone', 'club', 'club_name',
                  'is_licensed', 'license_number', 'license_expiry',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'email', 'created_at', 'updated_at']


class RiderDetailSerializer(serializers.ModelSerializer):
    """Detailed rider serializer with all information"""
    club = ClubListSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(read_only=True)
    races_participated = serializers.SerializerMethodField()
    
    class Meta:
        model = Rider
        fields = ['id', 'user', 'username', 'email', 'full_name',
                  'first_name', 'last_name', 'date_of_birth', 'photo', 
                  'phone', 'club', 'is_licensed', 'license_number', 
                  'license_expiry', 'bike_info', 'gear_info', 'emergency_contact',
                  'races_participated', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'email', 'created_at', 'updated_at']
    
    def get_races_participated(self, obj):
        return obj.race_participations.filter(status='confirmed').count()


class RiderWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating rider profiles"""
    
    class Meta:
        model = Rider
        fields = ['first_name', 'last_name', 'date_of_birth', 'photo', 
                  'phone', 'club', 'is_licensed', 'license_number', 
                  'license_expiry', 'bike_info', 'gear_info', 'emergency_contact']
    
    def create(self, validated_data):
        # User is set from the request context
        user = self.context['request'].user
        
        # Check if rider profile already exists
        if hasattr(user, 'rider_profile'):
            raise serializers.ValidationError("Rider profile already exists for this user.")
        
        rider = Rider.objects.create(user=user, **validated_data)
        
        # Update user's is_rider flag
        user.is_rider = True
        user.save()
        
        return rider

