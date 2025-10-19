from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Club
from .serializers import (
    ClubListSerializer, ClubSerializer, 
    ClubDetailSerializer, ClubWriteSerializer
)


class ClubViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing clubs
    List/detail: all authenticated users
    Create/Delete: system admins only
    Update: system admins or club admins
    """
    queryset = Club.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClubListSerializer
        elif self.action == 'retrieve':
            return ClubDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ClubWriteSerializer
        return ClubSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        # Only system admins can create clubs
        if not self.request.user.is_system_admin and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only system administrators can create clubs.")
        serializer.save()
    
    def perform_update(self, serializer):
        # System admins or club admins can update
        club = self.get_object()
        user = self.request.user
        if not (user.is_system_admin or user.is_staff or club.admins.filter(id=user.id).exists()):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only system administrators or club admins can update this club.")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only system admins can delete
        if not self.request.user.is_system_admin and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only system administrators can delete clubs.")
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def riders(self, request, pk=None):
        """Get all riders in this club"""
        club = self.get_object()
        from riders.serializers import RiderListSerializer
        serializer = RiderListSerializer(club.riders.all(), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def organized_races(self, request, pk=None):
        """Get all races organized by this club"""
        club = self.get_object()
        from races.serializers import RaceListSerializer
        serializer = RaceListSerializer(club.organized_races.all(), many=True)
        return Response(serializer.data)

