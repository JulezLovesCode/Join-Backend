"""
URL routing configuration for join_backend application.

This module defines how HTTP requests are mapped to Django views based on URL patterns.
It serves as the central routing mechanism for the entire application.

Documentation references:
- Django URL dispatcher: https://docs.djangoproject.com/en/5.1/topics/http/urls/

Pattern definition examples:
- Function-based views:
  from my_app import views
  path('route/', views.view_function, name='view_name')
  
- Class-based views:
  from other_app.views import ViewClass
  path('route/', ViewClass.as_view(), name='view_name')
  
- Including other URL configurations:
  from django.urls import include
  path('prefix/', include('app.urls'))
"""
from django.urls import path, include
from django.contrib import admin

def generateAdministrationRoutes():
    """
    Generate URL patterns for Django administration interface.
    
    Returns:
        list: URL patterns for admin site access
    """
    return [
        path('admin/', admin.site.urls),
    ]

def generateApplicationRoutes():
    """
    Generate URL patterns for main application API endpoints.
    
    Returns:
        list: URL patterns for application API
    """
    return [
        path('api/', include('core_api.urls')),
    ]

def generateAuthenticationRoutes():
    """
    Generate URL patterns for authentication functionality.
    
    Returns:
        list: URL patterns for user authentication
    """
    return [
        path('api/auth/', include('auth_module.api.urls')),
        path('api-auth', include('rest_framework.urls')),
    ]

def compileRoutingConfiguration():
    """
    Compile the complete URL routing configuration.
    
    This function assembles all URL patterns from different functional groups
    into a single list used by Django's URL dispatcher.
    
    Returns:
        list: Complete URL pattern configuration
    """
    routeGroups = [
        generateAdministrationRoutes(),
        generateApplicationRoutes(),
        generateAuthenticationRoutes(),
    ]
    
    # Flatten the list of route groups
    allRoutes = []
    for group in routeGroups:
        allRoutes.extend(group)
    
    return allRoutes

# The main URL patterns list used by Django's URL dispatcher
routePatterns = compileRoutingConfiguration()

# Export the URL patterns for Django to use
urlpatterns = routePatterns