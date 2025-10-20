from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import RaceDayResult, RaceResult, ChampionshipResult, ClubResult
from .serializers import (
    RaceDayResultSerializer, RaceResultSerializer,
    ChampionshipResultSerializer, ClubResultSerializer
)
from .calculations import recalculate_all


class RaceDayResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for race day results
    Read: all users (including anonymous)
    Create/Update/Delete: system admins or race organizers
    """
    queryset = RaceDayResult.objects.select_related('race_day__race', 'rider').all()
    serializer_class = RaceDayResultSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        user = self.request.user
        race_day = serializer.validated_data['race_day']
        race = race_day.race
        
        # Check if user is system admin or race organizer
        is_organizer = race.organizers.filter(admins=user).exists()
        
        if not (user.is_system_admin or user.is_staff or is_organizer):
            raise PermissionDenied("Only race organizers or administrators can submit results.")
        
        serializer.save()
    
    def perform_update(self, serializer):
        user = self.request.user
        result = self.get_object()
        race = result.race_day.race
        
        is_organizer = race.organizers.filter(admins=user).exists()
        
        if not (user.is_system_admin or user.is_staff or is_organizer):
            raise PermissionDenied("Only race organizers or administrators can update results.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        user = self.request.user
        race = instance.race_day.race
        
        is_organizer = race.organizers.filter(admins=user).exists()
        
        if not (user.is_system_admin or user.is_staff or is_organizer):
            raise PermissionDenied("Only race organizers or administrators can delete results.")
        
        instance.delete()


class RaceResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for overall race results
    Results are automatically calculated from race day results
    """
    queryset = RaceResult.objects.select_related('race', 'rider__club').all()
    serializer_class = RaceResultSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by race if provided
        race_id = self.request.query_params.get('race', None)
        if race_id:
            queryset = queryset.filter(race_id=race_id)
        
        # Filter by rider if provided
        rider_id = self.request.query_params.get('rider', None)
        if rider_id:
            queryset = queryset.filter(rider_id=rider_id)
        
        # Filter by category if provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def recalculate(self, request):
        """Manually trigger recalculation of all results"""
        race_id = request.data.get('race_id')
        
        if race_id:
            from races.models import Race
            race = Race.objects.get(id=race_id)
            recalculate_all(race=race)
            return Response({'status': 'Results recalculated for race'})
        
        return Response({'error': 'race_id required'}, status=status.HTTP_400_BAD_REQUEST)


class ChampionshipResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for championship standings
    Standings are automatically calculated from race results
    """
    queryset = ChampionshipResult.objects.select_related('championship', 'rider__club').all()
    serializer_class = ChampionshipResultSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by championship if provided
        championship_id = self.request.query_params.get('championship', None)
        if championship_id:
            queryset = queryset.filter(championship_id=championship_id)
        
        # Filter by rider if provided
        rider_id = self.request.query_params.get('rider', None)
        if rider_id:
            queryset = queryset.filter(rider_id=rider_id)
        
        # Filter by category if provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def recalculate(self, request):
        """Manually trigger recalculation of championship standings"""
        championship_id = request.data.get('championship_id')
        
        if championship_id:
            from championships.models import Championship
            championship = Championship.objects.get(id=championship_id)
            recalculate_all(championship=championship)
            return Response({'status': 'Championship standings recalculated'})
        
        return Response({'error': 'championship_id required'}, status=status.HTTP_400_BAD_REQUEST)


class ClubResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for club standings
    Standings are automatically calculated from rider results
    """
    queryset = ClubResult.objects.select_related('championship', 'club').all()
    serializer_class = ClubResultSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by championship if provided
        championship_id = self.request.query_params.get('championship', None)
        if championship_id:
            queryset = queryset.filter(championship_id=championship_id)
        
        return queryset

