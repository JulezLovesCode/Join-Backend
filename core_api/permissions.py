"""
Custom permission classes for the REST API.

This module provides specialized permission handling for controlling
access to API endpoints based on authentication status and request parameters.
"""
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

class AuthenticatedUserOrGuestAccessPermission(BasePermission):
    """
    Permission class that allows access to either authenticated users or guests with ID.
    
    This permission class enables API endpoints to be accessible by:
    1. Fully authenticated users with valid credentials
    2. Guest users who provide a valid guest identifier in query parameters
    
    This supports both authenticated flows and guest/anonymous access patterns
    with proper identification tracking.
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Determine if the request should be permitted access to the view.
        
        Args:
            request: The incoming HTTP request
            view: The view handling the request
            
        Returns:
            bool: True if access is permitted, False otherwise
        """
        if self._isAuthenticatedUser(request):
            return True
            
        return self._hasValidGuestIdentifier(request)
    
    def _isAuthenticatedUser(self, request: Request) -> bool:
        """
        Check if the request is from an authenticated user.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            bool: True if the user is authenticated, False otherwise
        """
        return request.user and request.user.is_authenticated
    
    def _hasValidGuestIdentifier(self, request: Request) -> bool:
        """
        Check if the request contains a valid guest identifier.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            bool: True if a guest_id is present, False otherwise
        """
        visitorIdentifier = request.query_params.get("guest_id")
        return bool(visitorIdentifier)

# For backward compatibility with existing code
IsAuthenticatedOrGuest = AuthenticatedUserOrGuestAccessPermission