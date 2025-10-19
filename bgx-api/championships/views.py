from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Championship
from .serializers import (
    ChampionshipListSerializer, ChampionshipSerializer,
    ChampionshipDetailSerializer, ChampionshipWriteSerializer
)


class ChampionshipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing championships
    List/detail: all users
    Create/Update/Delete: system admins only
    """
    queryset = Championship.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChampionshipListSerializer
        elif self.action == 'retrieve':
            return ChampionshipDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ChampionshipWriteSerializer
        return ChampionshipSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        if not self.request.user.is_system_admin and not self.request.user.is_staff:
            raise PermissionDenied("Only system administrators can create championships.")
        serializer.save()
    
    def perform_update(self, serializer):
        if not self.request.user.is_system_admin and not self.request.user.is_staff:
            raise PermissionDenied("Only system administrators can update championships.")
        serializer.save()
    
    def perform_destroy(self, instance):
        if not self.request.user.is_system_admin and not self.request.user.is_staff:
            raise PermissionDenied("Only system administrators can delete championships.")
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def races(self, request, pk=None):
        """Get all races in this championship"""
        championship = self.get_object()
        from races.serializers import RaceListSerializer
        serializer = RaceListSerializer(championship.races.all(), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def standings(self, request, pk=None):
        """Get championship standings"""
        championship = self.get_object()
        from results.serializers import ChampionshipResultSerializer
        from results.models import ChampionshipResult
        
        standings = ChampionshipResult.objects.filter(
            championship=championship
        ).order_by('-total_points', 'rider__last_name')
        
        serializer = ChampionshipResultSerializer(standings, many=True)
        return Response(serializer.data)

