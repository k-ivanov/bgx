from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_rider', 'is_club_admin', 'is_system_admin', 'is_activated', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'is_system_admin', 'is_activated']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Generate activation code automatically
        user.generate_activation_code()
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with additional info"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_rider', 'is_club_admin', 'is_system_admin', 'is_activated',
                  'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_system_admin', 'is_activated']


class UserActivationSerializer(serializers.Serializer):
    """Serializer for account activation"""
    activation_code = serializers.CharField(required=True, max_length=64)


class RiderMatchSerializer(serializers.Serializer):
    """Serializer for matching with existing rider"""
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    license_number = serializers.CharField(required=False, allow_blank=True, max_length=50)
    date_of_birth = serializers.DateField(required=False, allow_null=True)


class ClaimAccountSerializer(serializers.Serializer):
    """Serializer for claiming an existing user account"""
    rider_id = serializers.IntegerField(required=True)
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

