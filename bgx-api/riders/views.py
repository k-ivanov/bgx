from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Rider
from .serializers import (
    RiderListSerializer, RiderSerializer,
    RiderDetailSerializer, RiderWriteSerializer
)


class RiderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing riders
    List/detail: authenticated users
    Create: any authenticated user can create their own profile
    Update/Delete: only own profile or system admins
    """
    queryset = Rider.objects.select_related('user', 'club').all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RiderListSerializer
        elif self.action == 'retrieve':
            return RiderDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RiderWriteSerializer
        return RiderSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def perform_update(self, serializer):
        rider = self.get_object()
        user = self.request.user
        
        # Only owner or system admin can update
        if rider.user != user and not user.is_system_admin and not user.is_staff:
            raise PermissionDenied("You can only update your own rider profile.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        user = self.request.user
        
        # Only owner or system admin can delete
        if instance.user != user and not user.is_system_admin and not user.is_staff:
            raise PermissionDenied("You can only delete your own rider profile.")
        
        # Update user's is_rider flag
        instance.user.is_rider = False
        instance.user.save()
        
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get all race results for this rider"""
        rider = self.get_object()
        from results.serializers import RaceResultSerializer
        from results.models import RaceResult
        
        results = RaceResult.objects.filter(rider=rider).order_by('-race__start_date')
        serializer = RaceResultSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def upcoming_races(self, request, pk=None):
        """Get upcoming races for this rider"""
        rider = self.get_object()
        from races.serializers import RaceListSerializer
        from django.utils import timezone
        
        upcoming = rider.race_participations.filter(
            race__start_date__gte=timezone.now(),
            status='confirmed'
        ).select_related('race')
        
        races = [participation.race for participation in upcoming]
        serializer = RaceListSerializer(races, many=True)
        return Response(serializer.data)

