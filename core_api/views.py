from django.shortcuts import render
from django.db.models import Count, F, Sum, Case, When, IntegerField
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from core_api.models import (
    Task as WorkItem,
    Subtask as WorkItemComponent, 
    Contact as TeamMember
)

from .serializers import (
    TaskSerializer as WorkItemSerializer,
    SubtaskSerializer as WorkItemComponentSerializer, 
    ContactSerializer as TeamMemberSerializer
)

from .permissions import IsAuthenticatedOrGuest

class WorkItemManagementController(ModelViewSet):
    resource_collection = WorkItem.objects.all()
    data_transformer = WorkItemSerializer
    access_policy = [AllowAny]
    authentication_mechanisms = [TokenAuthentication]
    allowed_operations = ["get", "post", "put", "patch", "delete"]
    
    queryset = resource_collection
    serializer_class = data_transformer
    permission_classes = access_policy
    authentication_classes = authentication_mechanisms
    http_method_names = allowed_operations

    def retrieve_filtered_collection(self):
        workspace_category = self.request.query_params.get("board_category", None)
        if workspace_category:
            return WorkItem.objects.filter(board_category=workspace_category)
        return WorkItem.objects.all()

    def get_queryset(self):
        return self.retrieve_filtered_collection()

    def extract_team_member_ids(self):
        # Debug info - print all the request data
        print("\n\nTASK CREATE/UPDATE REQUEST DATA:", self.request.data, "\n\n")
        
        # Try multiple possible field names for maximum compatibility
        raw_ids = None
        for field in ["contact_ids", "member_assignments", "contacts"]:
            if field in self.request.data and self.request.data[field]:
                raw_ids = self.request.data[field]
                print(f"FOUND IDS IN FIELD: {field}")
                break
                
        if raw_ids is None:
            print("NO CONTACT IDS FOUND")
            return []
            
        # Debug
        print("EXTRACTED RAW IDS:", raw_ids)
        
        # Handle various formats
        if isinstance(raw_ids, (list, tuple, set)):
            # Convert all items to integers if possible
            result = []
            for item in raw_ids:
                try:
                    if isinstance(item, (int, float)) or (isinstance(item, str) and item.isdigit()):
                        result.append(int(item))
                    elif isinstance(item, dict) and 'id' in item and str(item['id']).isdigit():
                        result.append(int(item['id']))
                except (ValueError, TypeError):
                    pass
            print("PARSED IDS (LIST):", result)
            return result
            
        # Handle dictionary format
        if isinstance(raw_ids, dict):
            result = []
            for key, value in raw_ids.items():
                try:
                    if str(key).isdigit():
                        result.append(int(key))
                    elif isinstance(value, dict) and 'id' in value and str(value['id']).isdigit():
                        result.append(int(value['id']))
                except (ValueError, TypeError):
                    pass
            print("PARSED IDS (DICT):", result)
            return result
        
        # Handle string with comma separated values
        if isinstance(raw_ids, str) and ',' in raw_ids:
            try:
                result = [int(item.strip()) for item in raw_ids.split(',') if item.strip().isdigit()]
                print("PARSED IDS (STRING):", result)
                return result
            except (ValueError, TypeError):
                pass
                
        # Last resort: try to convert single value
        try:
            if isinstance(raw_ids, (int, float)) or (isinstance(raw_ids, str) and raw_ids.isdigit()):
                print("PARSED ID (SINGLE):", [int(raw_ids)])
                return [int(raw_ids)]
        except (ValueError, TypeError):
            pass
            
        print("FAILED TO PARSE IDS, RETURNING EMPTY LIST")
        return []

    def create_component_items(self, parent_item, component_data_list):
        if not component_data_list:
            print("No subtasks to create")
            return
            
        print(f"CREATING SUBTASKS FOR TASK {parent_item.id}: {component_data_list}")
        
        # Delete any existing subtasks first to avoid duplicates
        parent_item.components.all().delete()
            
        for component_data in component_data_list:
            # Ensure we only use the fields that exist on the model
            subtask_data = {}
            try:
                if isinstance(component_data, dict):
                    # Handle various possible field names
                    title = (
                        component_data.get('title') or 
                        component_data.get('name') or 
                        component_data.get('text') or 
                        'Untitled Subtask'
                    )
                    
                    completed = (
                        component_data.get('completed', False) or 
                        component_data.get('done', False) or 
                        component_data.get('finished', False) or 
                        False
                    )
                    
                    subtask_data['title'] = title
                    subtask_data['completed'] = completed
                    
                    # Create the subtask with cleaned data
                    subtask = WorkItemComponent.objects.create(parent_item=parent_item, **subtask_data)
                    print(f"Created subtask: {subtask.id} - {subtask.title}")
                elif isinstance(component_data, str):
                    # Handle simple string subtasks
                    subtask = WorkItemComponent.objects.create(
                        parent_item=parent_item,
                        title=component_data,
                        completed=False
                    )
                    print(f"Created string subtask: {subtask.id} - {subtask.title}")
            except Exception as e:
                print(f"ERROR creating subtask: {e}")

    def perform_create(self, serializer):
        created_item = serializer.save()
        created_item.contacts.set(self.extract_team_member_ids())
        
        component_items_data = self.request.data.get("subtasks", [])
        self.create_component_items(created_item, component_items_data)

    def handle_team_member_assignments(self, instance, team_member_ids):
        if isinstance(team_member_ids, list) and len(team_member_ids) > 0:
            instance.contacts.set(team_member_ids)

    def update_component_items(self, instance, component_data_list):
        if isinstance(component_data_list, list) and component_data_list:
            instance.components.all().delete()
            
            for component_data in component_data_list:
                if "title" in component_data and "completed" in component_data:
                    WorkItemComponent.objects.create(
                        parent_item=instance, 
                        title=component_data["title"], 
                        completed=component_data["completed"]
                    )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        team_member_ids = request.data.get("contact_ids", None)
        component_data_list = request.data.get("subtasks", [])
        priority_level = request.data.get("priority", instance.priority)
        
        if team_member_ids is not None:
            self.handle_team_member_assignments(instance, team_member_ids)

        self.update_component_items(instance, component_data_list)
        
        return super().partial_update(request, *args, **kwargs)

class WorkItemComponentController(viewsets.ModelViewSet):
    permission_policy = [IsAuthenticatedOrGuest]
    resource_collection = WorkItemComponent.objects.all()
    data_transformer = WorkItemComponentSerializer
    
    permission_classes = permission_policy
    queryset = resource_collection
    serializer_class = data_transformer

    def create_component(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    create = create_component

    def update_component(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    update = update_component

    def update_component_partially(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    partial_update = update_component_partially

    def remove_component(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    destroy = remove_component

class TeamMemberController(viewsets.ModelViewSet):
    resource_collection = TeamMember.objects.all()
    data_transformer = TeamMemberSerializer
    access_policy = [AllowAny]
    
    queryset = resource_collection
    serializer_class = data_transformer
    permission_classes = access_policy

class ProductivityMetricsView(APIView):
    
    def calculate_progress_metrics(self):
        total_work_items = WorkItem.objects.count()
        completed_work_items = WorkItem.objects.filter(board_category="done").count()
        pending_work_items = total_work_items - completed_work_items
        
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
        return {
            "to-do": WorkItem.objects.filter(board_category="to-do").count(),
            "in-progress": WorkItem.objects.filter(board_category="in-progress").count(),
            "await-feedback": WorkItem.objects.filter(board_category="await-feedback").count(),
            "done": WorkItem.objects.filter(board_category="done").count(),
        }
    
    def count_items_by_priority(self):
        return {
            "urgent": WorkItem.objects.filter(priority="urgent").count(),
        }
    
    def assemble_summary_data(self):
        progress_metrics = self.calculate_progress_metrics()
        status_counts = self.count_items_by_status()
        priority_counts = self.count_items_by_priority()
        
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
        summary_data = self.assemble_summary_data()
        return Response(summary_data)

class WorkspaceOverviewView(APIView):
    access_policy = [IsAuthenticated]
    permission_classes = access_policy
    
    def retrieve_workspace_data(self):
        return list(WorkItem.objects.all().values())
    
    def get(self, request):
        workspace_data = self.retrieve_workspace_data()
        return Response({"board": workspace_data})

TaskViewSet = WorkItemManagementController
SubtaskViewSet = WorkItemComponentController
ContactViewSet = TeamMemberController
SummaryView = ProductivityMetricsView
BoardView = WorkspaceOverviewView