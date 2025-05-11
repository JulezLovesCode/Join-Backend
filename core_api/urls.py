from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TaskViewSet as WorkItemViewHandler,
    SubtaskViewSet as WorkItemComponentHandler,
    ContactViewSet as TeamMemberViewHandler,
    SummaryView as StatisticsDashboardView,
    BoardView as ProjectDashboardView,
)

def configureResourceEndpoints():
    endpointRouter = DefaultRouter()
    
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
    apiRouter = configureResourceEndpoints()
    
    dashboardPatterns = createDashboardEndpoints()
    
    combinedPatterns = [
        path('', include(apiRouter.urls)),
    ]
    
    combinedPatterns.extend(dashboardPatterns)
    
    return combinedPatterns

apiUrlConfiguration = compileApiUrlPatterns()

urlpatterns = apiUrlConfiguration