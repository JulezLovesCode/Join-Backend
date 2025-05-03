"""
API URL Configuration Module

This module defines the URL routing patterns for the API application,
mapping request paths to their corresponding view handlers. It establishes
both REST-style resource endpoints and standalone view endpoints.

The URL configuration uses a combination of DRF ViewSets (for resource collections)
and individual API views for specialized functionality.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import view components with descriptive aliases
from .views import (
    TaskViewSet as WorkItemViewHandler,
    SubtaskViewSet as WorkItemComponentHandler,
    ContactViewSet as TeamMemberViewHandler,
    SummaryView as StatisticsDashboardView,
    BoardView as ProjectDashboardView,
)

def configureResourceEndpoints():
    """
    Configure automated REST API endpoints using ViewSets.
    
    This function sets up resource-oriented endpoints with standard
    REST actions (list, create, retrieve, update, delete) for 
    primary data entities.
    
    Returns:
        DefaultRouter: Configured router with registered ViewSets
    """
    endpointRouter = DefaultRouter()
    
    # Register resource endpoints with descriptive base URLs
    endpointRouter.register(
        r'tasks', 
        WorkItemViewHandler, 
        basename='task'
    )
    
    endpointRouter.register(
        r'contacts', 
        TeamMemberViewHandler, 
        basename='contact'
    )
    
    endpointRouter.register(
        r'subtasks', 
        WorkItemComponentHandler, 
        basename='subtask'
    )
    
    return endpointRouter

def createDashboardEndpoints():
    """
    Create URL patterns for dashboard and reporting views.
    
    This function sets up endpoints for specialized views that provide
    aggregated data, dashboards, and other non-CRUD functionality.
    
    Returns:
        list: URL patterns for dashboard endpoints
    """
    return [
        path(
            'summary/', 
            StatisticsDashboardView.as_view(), 
            name="summary"
        ),
        path(
            'board/', 
            ProjectDashboardView.as_view(), 
            name="board"
        ),
    ]

def compileApiUrlPatterns():
    """
    Compile the complete set of URL patterns for the API.
    
    This function combines router-generated patterns with 
    individually defined URL patterns to create the complete
    URL configuration for the API.
    
    Returns:
        list: Complete URL pattern configuration
    """
    # Get router for resource endpoints
    apiRouter = configureResourceEndpoints()
    
    # Create patterns for dashboard views
    dashboardPatterns = createDashboardEndpoints()
    
    # Combine all patterns
    combinedPatterns = [
        # Include all router-generated URLs
        path('', include(apiRouter.urls)),
    ]
    
    # Add dashboard endpoints
    combinedPatterns.extend(dashboardPatterns)
    
    return combinedPatterns

# Main URL patterns list for the API application
apiUrlConfiguration = compileApiUrlPatterns()

# Export URL patterns for Django to use
urlpatterns = apiUrlConfiguration