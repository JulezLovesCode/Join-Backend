from django.urls import path, include
from django.contrib import admin
from .admin import no_login_admin_site
from core_api.custom_admin import (
    custom_admin_dashboard,
    custom_admin_tasks,
    custom_admin_contacts,
    custom_admin_users,
    custom_admin_boards,
    custom_admin_subtasks
)

def generateAdministrationRoutes():
    return [
        path('admin/', admin.site.urls),
        path('no-login-admin/', no_login_admin_site.urls),
        # Custom admin routes that don't require login
        path('custom-admin/', custom_admin_dashboard, name='custom_admin_dashboard'),
        path('custom-admin/tasks/', custom_admin_tasks, name='custom_admin_tasks'),
        path('custom-admin/contacts/', custom_admin_contacts, name='custom_admin_contacts'),
        path('custom-admin/users/', custom_admin_users, name='custom_admin_users'),
        path('custom-admin/boards/', custom_admin_boards, name='custom_admin_boards'),
        path('custom-admin/subtasks/', custom_admin_subtasks, name='custom_admin_subtasks'),
    ]

def generateApplicationRoutes():
    return [
        path('api/', include('core_api.urls')),
    ]

def generateAuthenticationRoutes():
    return [
        path('api/auth/', include('auth_module.api.urls')),
        path('api-auth', include('rest_framework.urls')),
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