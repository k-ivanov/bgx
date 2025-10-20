from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer, 
    UserDetailSerializer, UserActivationSerializer,
    RiderMatchSerializer, ClaimAccountSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['retrieve', 'me']:
            return UserDetailSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'match_rider', 'claim_account', 'activate']:
            return [permissions.AllowAny()]
        elif self.action == 'me':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    def get_authenticators(self):
        """
        Remove SessionAuthentication for public endpoints to avoid CSRF issues.
        For unauthenticated POST requests, use only JWT authentication.
        """
        from rest_framework_simplejwt.authentication import JWTAuthentication
        # Only use JWT for public endpoints (no session auth to avoid CSRF issues)
        return [JWTAuthentication()]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user info"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Register a new user"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'activation_code': user.activation_code,
            'message': 'Registration successful! Please use the activation code to activate your account.'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def activate(self, request):
        """Activate a user account with activation code"""
        serializer = UserActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        activation_code = serializer.validated_data['activation_code']
        
        try:
            user = User.objects.get(activation_code=activation_code)
        except User.DoesNotExist:
            raise ValidationError({'activation_code': 'Invalid activation code'})
        
        if user.is_activated:
            raise ValidationError({'activation_code': 'Account is already activated'})
        
        # Activate the user
        user.activate()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Account activated successfully!',
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def match_rider(self, request):
        """Match user input with existing riders in the system"""
        from riders.models import Rider
        from riders.serializers import RiderSerializer
        
        serializer = RiderMatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        license_number = serializer.validated_data.get('license_number', '')
        date_of_birth = serializer.validated_data.get('date_of_birth')
        
        # Build query to find matching riders
        from django.db.models import Q
        
        query = Q(first_name__iexact=first_name) & Q(last_name__iexact=last_name)
        
        # Find riders with unclaimed accounts
        riders = Rider.objects.filter(query).select_related('user', 'club')
        
        # Further filter by license number if provided
        if license_number:
            riders = riders.filter(license_number__iexact=license_number)
        
        # Further filter by date of birth if provided
        if date_of_birth:
            riders = riders.filter(date_of_birth=date_of_birth)
        
        # Only show riders whose user accounts are not claimed
        riders = riders.filter(user__is_claimed=False)
        
        if not riders.exists():
            return Response({
                'matches': [],
                'message': 'No matching riders found. Please check your information or contact an administrator.'
            }, status=status.HTTP_200_OK)
        
        # Return matching riders
        rider_data = []
        for rider in riders:
            rider_data.append({
                'id': rider.id,
                'first_name': rider.first_name,
                'last_name': rider.last_name,
                'license_number': rider.license_number,
                'club': rider.club.name if rider.club else None,
                'is_licensed': rider.is_licensed,
                'username': rider.user.username,
            })
        
        return Response({
            'matches': rider_data,
            'message': f'Found {len(rider_data)} matching rider(s)'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def claim_account(self, request):
        """Claim an existing user account by matching with a rider"""
        from riders.models import Rider
        
        serializer = ClaimAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rider_id = serializer.validated_data['rider_id']
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        email = serializer.validated_data['email']
        
        # Get the rider
        try:
            rider = Rider.objects.select_related('user').get(id=rider_id)
        except Rider.DoesNotExist:
            raise ValidationError({'rider_id': 'Rider not found'})
        
        user = rider.user
        
        # Check if already claimed
        if user.is_claimed:
            raise ValidationError({'rider_id': 'This account has already been claimed'})
        
        # Check if username is available (not same as current placeholder username)
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            raise ValidationError({'username': 'This username is already taken'})
        
        # Check if email is available
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            raise ValidationError({'email': 'This email is already registered'})
        
        # Update user account
        user.username = username
        user.email = email
        user.set_password(password)
        user.is_claimed = True
        user.is_rider = True
        
        # Generate activation code
        user.generate_activation_code()
        user.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'rider': {
                'id': rider.id,
                'first_name': rider.first_name,
                'last_name': rider.last_name,
                'license_number': rider.license_number,
                'club': rider.club.name if rider.club else None,
            },
            'activation_code': user.activation_code,
            'message': 'Account claimed successfully! Please use the activation code to activate your account.'
        }, status=status.HTTP_200_OK)

