from rest_framework import serializers
from .models import Club


class ClubListSerializer(serializers.ModelSerializer):
    """Minimal serializer for club lists"""
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Club
        fields = ['id', 'name', 'logo', 'city', 'country', 'member_count']
    
    def get_member_count(self, obj):
        return obj.riders.count()


class ClubSerializer(serializers.ModelSerializer):
    """Standard club serializer"""
    member_count = serializers.SerializerMethodField()
    admin_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Club
        fields = ['id', 'name', 'description', 'logo', 'founded_date',
                  'contact_email', 'phone', 'website',
                  'address_line1', 'address_line2', 'city', 'state', 
                  'postal_code', 'country', 'member_count', 'admin_count',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'member_count', 'admin_count']
    
    def get_member_count(self, obj):
        return obj.riders.count()
    
    def get_admin_count(self, obj):
        return obj.admins.count()


class ClubDetailSerializer(serializers.ModelSerializer):
    """Detailed club serializer with relationships"""
    admins = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    organized_races_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Club
        fields = ['id', 'name', 'description', 'logo', 'founded_date',
                  'contact_email', 'phone', 'website',
                  'address_line1', 'address_line2', 'city', 'state', 
                  'postal_code', 'country', 'admins', 'member_count',
                  'organized_races_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_admins(self, obj):
        from accounts.serializers import UserSerializer
        return UserSerializer(obj.admins.all(), many=True).data
    
    def get_member_count(self, obj):
        return obj.riders.count()
    
    def get_organized_races_count(self, obj):
        return obj.organized_races.count()


class ClubWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating clubs"""
    admin_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Club
        fields = ['name', 'description', 'logo', 'founded_date',
                  'contact_email', 'phone', 'website',
                  'address_line1', 'address_line2', 'city', 'state', 
                  'postal_code', 'country', 'admin_ids']
    
    def create(self, validated_data):
        admin_ids = validated_data.pop('admin_ids', [])
        club = Club.objects.create(**validated_data)
        if admin_ids:
            from accounts.models import User
            club.admins.set(User.objects.filter(id__in=admin_ids))
        return club
    
    def update(self, instance, validated_data):
        admin_ids = validated_data.pop('admin_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if admin_ids is not None:
            from accounts.models import User
            instance.admins.set(User.objects.filter(id__in=admin_ids))
        
        return instance

