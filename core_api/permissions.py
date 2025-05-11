from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

class AuthenticatedUserOrGuestAccessPermission(BasePermission):
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        if self._isAuthenticatedUser(request):
            return True
            
        return self._hasValidGuestIdentifier(request)
    
    def _isAuthenticatedUser(self, request: Request) -> bool:
        return request.user and request.user.is_authenticated
    
    def _hasValidGuestIdentifier(self, request: Request) -> bool:
        visitorIdentifier = request.query_params.get("guest_id")
        return bool(visitorIdentifier)

IsAuthenticatedOrGuest = AuthenticatedUserOrGuestAccessPermission