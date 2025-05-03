"""
API View Handlers Module

This module defines view classes that handle API requests and responses
for the application. It includes resource controllers for data entities
and specialized view handlers for analytics and dashboards.

The views implement various access patterns including:
- RESTful CRUD operations for primary resources
- Filtered queries based on request parameters
- Aggregated statistics and summaries
- Custom data manipulation operations
"""
from django.shortcuts import render
from django.db.models import Count, F, Sum, Case, When, IntegerField
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

# Import models with semantic aliases
from core_api.models import (
    Task as WorkItem,
    Subtask as WorkItemComponent, 
    Contact as TeamMember
)

# Import serializers with semantic aliases
from .serializers import (
    TaskSerializer as WorkItemSerializer,
    SubtaskSerializer as WorkItemComponentSerializer, 
    ContactSerializer as TeamMemberSerializer
)

# Import custom permissions
from .permissions import IsAuthenticatedOrGuest

class WorkItemManagementController(ModelViewSet):
    """
    Controller for managing work items (tasks) in the system.
    
    This controller provides endpoints for creating, retrieving, updating,
    and deleting work items, with support for filtering, relationships,
    and nested resource management.
    """
    # Configuration properties
    resource_collection = WorkItem.objects.all()
    data_transformer = WorkItemSerializer
    access_policy = [AllowAny]
    authentication_mechanisms = [TokenAuthentication]
    allowed_operations = ["get", "post", "put", "patch", "delete"]
    
    # Map configuration to DRF expected properties
    queryset = resource_collection
    serializer_class = data_transformer
    permission_classes = access_policy
    authentication_classes = authentication_mechanisms
    http_method_names = allowed_operations

    def retrieve_filtered_collection(self):
        """
        Retrieve a filtered collection of work items based on query parameters.
        
        Returns:
            QuerySet: Filtered collection of work items
        """
        workspace_category = self.request.query_params.get("board_category", None)
        if workspace_category:
            return WorkItem.objects.filter(board_category=workspace_category)
        return WorkItem.objects.all()

    def get_queryset(self):
        """
        Get the queryset for this viewset, with applied filters.
        
        Returns:
            QuerySet: Filtered collection of work items
        """
        return self.retrieve_filtered_collection()

    def extract_team_member_ids(self):
        """
        Extract and validate team member IDs from request data.
        
        Returns:
            list: Valid team member IDs
        """
        raw_ids = self.request.data.get("contact_ids", [])
        
        if isinstance(raw_ids, (list, tuple, set)):
            return list(raw_ids)
        
        # Convert string IDs to integers if needed
        return [int(item_id) for item_id in raw_ids if str(item_id).isdigit()]

    def create_component_items(self, parent_item, component_data_list):
        """
        Create component items (subtasks) for a parent work item.
        
        Args:
            parent_item: The parent work item
            component_data_list: List of component data dictionaries
        """
        for component_data in component_data_list:
            WorkItemComponent.objects.create(parent_item=parent_item, **component_data)

    def perform_create(self, serializer):
        """
        Perform custom operations when creating a work item.
        
        This method handles the creation of the work item and its relationships
        to team members and component items.
        
        Args:
            serializer: The serializer instance
        """
        # Create the parent item and set team member relationships
        created_item = serializer.save()
        created_item.contacts.set(self.extract_team_member_ids())
        
        # Create any component items
        component_items_data = self.request.data.get("subtasks", [])
        self.create_component_items(created_item, component_items_data)

    def handle_team_member_assignments(self, instance, team_member_ids):
        """
        Update team member assignments for a work item.
        
        Args:
            instance: The work item instance
            team_member_ids: List of team member IDs to assign
        """
        if isinstance(team_member_ids, list) and len(team_member_ids) > 0:
            instance.contacts.set(team_member_ids)

    def update_component_items(self, instance, component_data_list):
        """
        Update component items for a work item.
        
        This method replaces existing components with new ones based on the provided data.
        
        Args:
            instance: The parent work item
            component_data_list: List of component data dictionaries
        """
        if isinstance(component_data_list, list) and component_data_list:
            # Remove existing components
            instance.components.all().delete()
            
            # Create new components
            for component_data in component_data_list:
                if "title" in component_data and "completed" in component_data:
                    WorkItemComponent.objects.create(
                        parent_item=instance, 
                        title=component_data["title"], 
                        completed=component_data["completed"]
                    )

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a work item with related entities.
        
        This method handles updating a work item and its relationships
        to team members and component items.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response: The API response
        """
        instance = self.get_object()
        
        # Extract data from request
        team_member_ids = request.data.get("contact_ids", None)
        component_data_list = request.data.get("subtasks", [])
        priority_level = request.data.get("priority", instance.priority)
        
        # Update team member assignments if provided
        if team_member_ids is not None:
            self.handle_team_member_assignments(instance, team_member_ids)

        # Update component items if provided
        self.update_component_items(instance, component_data_list)
        
        # Perform standard update operations
        return super().partial_update(request, *args, **kwargs)

class WorkItemComponentController(viewsets.ModelViewSet):
    """
    Controller for managing work item components (subtasks) in the system.
    
    This controller provides endpoints for creating, retrieving, updating,
    and deleting work item components, with appropriate permissions and
    validation.
    """
    permission_policy = [IsAuthenticatedOrGuest]
    resource_collection = WorkItemComponent.objects.all()
    data_transformer = WorkItemComponentSerializer
    
    # Map to DRF expected properties
    permission_classes = permission_policy
    queryset = resource_collection
    serializer_class = data_transformer

    def create_component(self, request, *args, **kwargs):
        """
        Create a new work item component.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response: The API response
        """
        return super().create(request, *args, **kwargs)
    
    # Map method to expected name for consistency with original
    create = create_component

    def update_component(self, request, *args, **kwargs):
        """
        Update an existing work item component.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response: The API response
        """
        return super().update(request, *args, **kwargs)
    
    # Map method to expected name for consistency with original
    update = update_component

    def update_component_partially(self, request, *args, **kwargs):
        """
        Partially update an existing work item component.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response: The API response
        """
        return super().partial_update(request, *args, **kwargs)
    
    # Map method to expected name for consistency with original
    partial_update = update_component_partially

    def remove_component(self, request, *args, **kwargs):
        """
        Remove an existing work item component.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response: The API response
        """
        return super().destroy(request, *args, **kwargs)
    
    # Map method to expected name for consistency with original
    destroy = remove_component

class TeamMemberController(viewsets.ModelViewSet):
    """
    Controller for managing team members (contacts) in the system.
    
    This controller provides endpoints for creating, retrieving, updating,
    and deleting team members, with appropriate permissions and validation.
    """
    resource_collection = TeamMember.objects.all()
    data_transformer = TeamMemberSerializer
    access_policy = [AllowAny]
    
    # Map to DRF expected properties
    queryset = resource_collection
    serializer_class = data_transformer
    permission_classes = access_policy

class ProductivityMetricsView(APIView):
    """
    View for retrieving productivity metrics and summaries.
    
    This view provides aggregated statistics about work items,
    including counts by status, priority, and completion rates.
    """
    
    def calculate_progress_metrics(self):
        """
        Calculate progress metrics for work items.
        
        Returns:
            dict: Dictionary of calculated metrics
        """
        # Count total and completed work items
        total_work_items = WorkItem.objects.count()
        completed_work_items = WorkItem.objects.filter(status="done").count()
        pending_work_items = total_work_items - completed_work_items
        
        # Calculate completion percentage
        completion_percentage = 0
        if total_work_items > 0:
            completion_percentage = round((completed_work_items / total_work_items * 100), 2)
        
        return {
            "total_work_items": total_work_items,
            "completed_work_items": completed_work_items,
            "pending_work_items": pending_work_items,
            "completion_percentage": completion_percentage
        }
    
    def count_items_by_status(self):
        """
        Count work items by status.
        
        Returns:
            dict: Dictionary of counts by status
        """
        return {
            "to-do": WorkItem.objects.filter(status="to-do").count(),
            "in-progress": WorkItem.objects.filter(status="in-progress").count(),
            "await-feedback": WorkItem.objects.filter(status="await-feedback").count(),
            "done": WorkItem.objects.filter(status="done").count(),
        }
    
    def count_items_by_priority(self):
        """
        Count work items by priority.
        
        Returns:
            dict: Dictionary of counts by priority
        """
        return {
            "urgent": WorkItem.objects.filter(priority="urgent").count(),
        }
    
    def assemble_summary_data(self):
        """
        Assemble all summary data into a single response.
        
        Returns:
            dict: Complete summary data dictionary
        """
        # Get metrics from component methods
        progress_metrics = self.calculate_progress_metrics()
        status_counts = self.count_items_by_status()
        priority_counts = self.count_items_by_priority()
        
        # Assemble the complete response
        summary_data = {
            "to-do": status_counts["to-do"],
            "in-progress": status_counts["in-progress"],
            "await-feedback": status_counts["await-feedback"],
            "done": progress_metrics["completed_work_items"],
            "total-tasks": progress_metrics["total_work_items"],
            "urgent": priority_counts["urgent"],
            "completed-percentage": progress_metrics["completion_percentage"],
        }
        
        return summary_data
    
    def get(self, request):
        """
        Handle GET requests for summary data.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response: The API response with summary data
        """
        summary_data = self.assemble_summary_data()
        return Response(summary_data)

class WorkspaceOverviewView(APIView):
    """
    View for retrieving board/workspace overview data.
    
    This view provides a comprehensive view of all work items
    organized for board display.
    """
    access_policy = [IsAuthenticated]
    permission_classes = access_policy
    
    def retrieve_workspace_data(self):
        """
        Retrieve all work items for workspace display.
        
        Returns:
            list: List of work item data dictionaries
        """
        return list(WorkItem.objects.all().values())
    
    def get(self, request):
        """
        Handle GET requests for workspace data.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response: The API response with workspace data
        """
        workspace_data = self.retrieve_workspace_data()
        return Response({"board": workspace_data})

# Legacy class names for backward compatibility
TaskViewSet = WorkItemManagementController
SubtaskViewSet = WorkItemComponentController
ContactViewSet = TeamMemberController
SummaryView = ProductivityMetricsView
BoardView = WorkspaceOverviewView