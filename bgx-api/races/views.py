from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from .models import Race, RaceDay, RaceParticipation
from .serializers import (
    RaceListSerializer, RaceSerializer, RaceDetailSerializer,
    RaceWriteSerializer, RaceDaySerializer, RaceParticipationSerializer,
    RaceSignupSerializer
)


class RaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing races
    List/detail: all users
    Create/Update/Delete: system admins or club admins
    """
    queryset = Race.objects.prefetch_related('organizers', 'championships', 'race_days').all()
    filterset_fields = ['championships', 'status', 'location']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RaceListSerializer
        elif self.action == 'retrieve':
            return RaceDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RaceWriteSerializer
        elif self.action == 'signup':
            return RaceSignupSerializer
        return RaceSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'participants', 'results']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_system_admin and not user.is_staff and not user.is_club_admin:
            raise PermissionDenied("Only system administrators or club administrators can create races.")
        serializer.save()
    
    def perform_update(self, serializer):
        race = self.get_object()
        user = self.request.user
        
        # Check if user is system admin, staff, or organizer of this race
        is_organizer = race.organizers.filter(admins=user).exists()
        
        if not (user.is_system_admin or user.is_staff or is_organizer):
            raise PermissionDenied("You don't have permission to update this race.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        if not self.request.user.is_system_admin and not self.request.user.is_staff:
            raise PermissionDenied("Only system administrators can delete races.")
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def signup(self, request, pk=None):
        """Sign up a rider for this race"""
        race = self.get_object()
        
        # Check if user has a rider profile
        if not hasattr(request.user, 'rider_profile'):
            raise ValidationError("You must have a rider profile to sign up for races.")
        
        rider = request.user.rider_profile
        
        # Check if registration is open
        if not race.registration_open:
            raise ValidationError("Registration is not open for this race.")
        
        # Check registration deadline
        if race.registration_deadline and timezone.now().date() > race.registration_deadline:
            raise ValidationError("Registration deadline has passed.")
        
        # Check if already registered
        if RaceParticipation.objects.filter(race=race, rider=rider).exists():
            raise ValidationError("You are already registered for this race.")
        
        # Check max participants
        if race.max_participants:
            confirmed_count = race.participations.filter(status='confirmed').count()
            if confirmed_count >= race.max_participants:
                raise ValidationError("This race has reached maximum participants.")
        
        serializer = RaceSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        participation = RaceParticipation.objects.create(
            race=race,
            rider=rider,
            category=serializer.validated_data['category'],
            status='confirmed'
        )
        
        return Response(
            RaceParticipationSerializer(participation).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Get all participants in this race"""
        race = self.get_object()
        participations = race.participations.filter(status='confirmed').select_related('rider')
        serializer = RaceParticipationSerializer(participations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get race results"""
        race = self.get_object()
        from results.serializers import RaceResultSerializer
        from results.models import RaceResult
        
        results = RaceResult.objects.filter(race=race).order_by('overall_position')
        serializer = RaceResultSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def days(self, request, pk=None):
        """Get or create race days"""
        race = self.get_object()
        
        if request.method == 'GET':
            serializer = RaceDaySerializer(race.race_days.all(), many=True)
            return Response(serializer.data)
        else:
            # Check permissions
            user = request.user
            is_organizer = race.organizers.filter(admins=user).exists()
            
            if not (user.is_system_admin or user.is_staff or is_organizer):
                raise PermissionDenied("You don't have permission to create race days.")
            
            serializer = RaceDaySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(race=race)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class RaceDayViewSet(viewsets.ModelViewSet):
    """ViewSet for managing individual race days"""
    queryset = RaceDay.objects.select_related('race').all()
    serializer_class = RaceDaySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_update(self, serializer):
        race_day = self.get_object()
        user = self.request.user
        
        is_organizer = race_day.race.organizers.filter(admins=user).exists()
        
        if not (user.is_system_admin or user.is_staff or is_organizer):
            raise PermissionDenied("You don't have permission to update this race day.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        user = self.request.user
        is_organizer = instance.race.organizers.filter(admins=user).exists()
        
        if not (user.is_system_admin or user.is_staff or is_organizer):
            raise PermissionDenied("You don't have permission to delete this race day.")
        
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get results for this race day"""
        race_day = self.get_object()
        from results.serializers import RaceDayResultSerializer
        from results.models import RaceDayResult
        
        results = RaceDayResult.objects.filter(race_day=race_day).order_by('position')
        serializer = RaceDayResultSerializer(results, many=True)
        return Response(serializer.data)


class RaceParticipationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing race participations"""
    queryset = RaceParticipation.objects.select_related('race', 'rider').all()
    serializer_class = RaceParticipationSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def perform_update(self, serializer):
        participation = self.get_object()
        user = self.request.user
        
        # Riders can update their own participation, organizers can update any
        is_organizer = participation.race.organizers.filter(admins=user).exists()
        is_owner = participation.rider.user == user
        
        if not (user.is_system_admin or user.is_staff or is_organizer or is_owner):
            raise PermissionDenied("You don't have permission to update this participation.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        user = self.request.user
        is_organizer = instance.race.organizers.filter(admins=user).exists()
        is_owner = instance.rider.user == user
        
        if not (user.is_system_admin or user.is_staff or is_organizer or is_owner):
            raise PermissionDenied("You don't have permission to delete this participation.")
        
        instance.delete()

