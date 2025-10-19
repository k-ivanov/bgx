"""
Custom permission classes for the BGX API
"""
from rest_framework import permissions


class IsSystemAdmin(permissions.BasePermission):
    """
    Permission class that only allows system administrators
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_system_admin or request.user.is_staff
        )


class IsClubAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows club admins to modify their club's content
    Read permissions are allowed to any authenticated user
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated and (
            request.user.is_club_admin or 
            request.user.is_system_admin or 
            request.user.is_staff
        )
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # System admins can do anything
        if request.user.is_system_admin or request.user.is_staff:
            return True
        
        # Club admins can only modify their own club
        if hasattr(obj, 'admins'):
            return obj.admins.filter(id=request.user.id).exists()
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows users to only modify their own data
    Read permissions are allowed to any authenticated user
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # System admins can do anything
        if request.user.is_system_admin or request.user.is_staff:
            return True
        
        # Check if object has a user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsRaceOrganizer(permissions.BasePermission):
    """
    Permission class that allows race organizers to manage race details
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # System admins can do anything
        if request.user.is_system_admin or request.user.is_staff:
            return True
        
        # Check if user is an organizer of the race
        if hasattr(obj, 'race'):
            race = obj.race
        elif hasattr(obj, 'organizers'):
            race = obj
        else:
            return False
        
        return race.organizers.filter(admins=request.user).exists()

