from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer, 
    UserDetailSerializer, UserActivationSerializer
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
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action == 'me':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
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

