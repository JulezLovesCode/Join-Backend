"""
Admin site configuration for API models.

This module registers the application's models with the Django admin interface,
enabling administrative access to database records through a web interface.
"""
from django.contrib import admin
from django.apps import apps

# Import model components from current package 
from .models import (
    Task as TaskModel,
    Subtask as SubtaskModel, 
    Contact as ContactModel
)

class AdminRegistrationManager:
    """
    Handles the registration of models with the Django admin interface.
    
    This class provides methods for registering models individually or in groups,
    centralizing the admin configuration process.
    """
    
    def __init__(self):
        """Initialize the registration manager."""
        self.adminSite = admin.site
        
    def registerTaskComponents(self):
        """
        Register task-related models with the admin interface.
        
        This includes the main Task model and its related Subtask model.
        """
        self.adminSite.register(TaskModel)
        self.adminSite.register(SubtaskModel)
    
    def registerUserComponents(self):
        """
        Register user-related models with the admin interface.
        
        This includes the Contact model and potential future user-related models.
        """
        self.adminSite.register(ContactModel)
    
    def executeRegistration(self):
        """
        Execute the complete registration process for all application models.
        
        This method calls all the specialized registration methods to ensure
        that all models are properly registered with the admin interface.
        """
        self.registerTaskComponents()
        self.registerUserComponents()

def configureAdminInterface():
    """
    Configure the Django admin interface with all application models.
    
    This function initializes the registration manager and executes
    the model registration process.
    """
    registrationManager = AdminRegistrationManager()
    registrationManager.executeRegistration()

# Execute the admin configuration process
configureAdminInterface()