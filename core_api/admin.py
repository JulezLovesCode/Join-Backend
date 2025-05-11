from django.contrib import admin
from django.apps import apps

from .models import (
    Task as TaskModel,
    Subtask as SubtaskModel, 
    Contact as ContactModel
)

class AdminRegistrationManager:
    
    def __init__(self):
        self.adminSite = admin.site
        
    def registerTaskComponents(self):
        self.adminSite.register(TaskModel)
        self.adminSite.register(SubtaskModel)
    
    def registerUserComponents(self):
        self.adminSite.register(ContactModel)
    
    def executeRegistration(self):
        self.registerTaskComponents()
        self.registerUserComponents()

def configureAdminInterface():
    registrationManager = AdminRegistrationManager()
    registrationManager.executeRegistration()

configureAdminInterface()