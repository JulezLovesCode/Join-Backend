"""
User Authentication Administration Module

This module configures the Django admin interface for managing user accounts
and authentication. It registers custom user models with the admin interface
and configures the appropriate admin views and permissions.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import CustomUser as AuthenticationUser


class UserAuthenticationAdminConfiguration:
    """
    Configuration handler for user authentication admin interface.
    
    This class centralizes the registration of authentication-related
    models with the Django admin interface and configures their
    presentation and management capabilities.
    """
    
    def __init__(self):
        """Initialize the admin configuration handler."""
        self.admin_site = admin.site
        self.user_admin_class = DjangoUserAdmin
    
    def register_authentication_models(self):
        """
        Register all authentication-related models with the admin interface.
        
        This method configures how user accounts and related authentication
        models appear and function in the Django admin interface.
        """
        self.register_user_model()
    
    def register_user_model(self):
        """
        Register the custom user model with appropriate admin configuration.
        
        This registration uses Django's built-in UserAdmin class to provide
        a full-featured interface for managing user accounts, including
        list views, detail forms, and permission management.
        """
        self.admin_site.register(AuthenticationUser, self.user_admin_class)


def configure_authentication_admin():
    """
    Configure the admin interface for authentication management.
    
    This function initializes and executes the admin configuration process
    for all authentication-related models.
    """
    admin_config = UserAuthenticationAdminConfiguration()
    admin_config.register_authentication_models()


# Execute the admin configuration
configure_authentication_admin()