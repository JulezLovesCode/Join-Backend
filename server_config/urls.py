from django.urls import path, include
from django.contrib import admin
from .admin import no_login_admin_site

def generateAdministrationRoutes():
    return [
        path('admin/', admin.site.urls),
        path('no-login-admin/', no_login_admin_site.urls),
    ]

def generateApplicationRoutes():
    return [
        path('api/', include('core_api.urls')),
    ]

def generateAuthenticationRoutes():
    return [
        path('api/auth/', include('auth_module.api.urls')),
        path('api-auth/', include('rest_framework.urls')),
    ]

def compileRoutingConfiguration():
    routeGroups = [
        generateAdministrationRoutes(),
        generateApplicationRoutes(),
        generateAuthenticationRoutes(),
    ]
    
    allRoutes = []
    for group in routeGroups:
        allRoutes.extend(group)
    
    return allRoutes

routePatterns = compileRoutingConfiguration()

urlpatterns = routePatterns