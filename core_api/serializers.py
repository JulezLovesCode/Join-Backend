"""
API Serialization Module

This module defines the serializers that transform between the application's
internal data models and their external representations for the REST API.
Serializers handle validation, conversion, and relationship management
for all data structures exposed through the API.
"""
from rest_framework import serializers
from typing import Dict, List, Any, Optional

# Import models with aliased names for clarity
from core_api.models import (
    Task as TaskModel,
    Subtask as SubtaskModel,
    Contact as TeamMemberModel,
    Board as ProjectModel
)

class TeamMemberDataSerializer(serializers.ModelSerializer):
    """
    Serializer for team member data.
    
    Handles conversion between TeamMember model instances and their
    JSON representation for API responses and requests.
    """
    
    def validate_email(self, value: str) -> str:
        """
        Perform additional validation on email addresses.
        
        Args:
            value: The email address to validate
            
        Returns:
            The validated email address
        """
        # Additional validation could be added here if needed
        return value
    
    class Meta:
        """Configuration for the serializer."""
        model = TeamMemberModel
        fields = '__all__'
        
        # Optional additional configurations
        read_only_fields = ['id']

class ProjectWorkspaceSerializer(serializers.ModelSerializer):
    """
    Serializer for project workspace data.
    
    Handles conversion between Project model instances and their
    JSON representation for API responses and requests.
    """
    
    class Meta:
        """Configuration for the serializer."""
        model = ProjectModel
        fields = '__all__'

class WorkItemComponentSerializer(serializers.ModelSerializer):
    """
    Serializer for work item component data.
    
    Handles conversion between WorkItemComponent model instances and their
    JSON representation for API responses and requests.
    """
    
    def validate_title(self, value: str) -> str:
        """
        Validate the component title.
        
        Args:
            value: The title to validate
            
        Returns:
            The validated title
        """
        # Could add custom validation rules here
        return value
    
    class Meta:
        """Configuration for the serializer."""
        model = SubtaskModel
        fields = '__all__'

class WorkItemDataSerializer(serializers.ModelSerializer):
    """
    Serializer for work item data.
    
    Handles conversion between WorkItem model instances and their
    JSON representation for API responses and requests. Manages related
    entities like team members and components.
    """
    
    # Nested relationship representations
    assigned_members = TeamMemberDataSerializer(
        source="contacts",
        many=True, 
        read_only=True
    )
    
    member_assignments = serializers.PrimaryKeyRelatedField(
        source="contacts",
        many=True,
        queryset=TeamMemberModel.objects.all(),
        write_only=False
    )
    
    task_components = WorkItemComponentSerializer(
        source="components",
        many=True, 
        read_only=True, 
        default=list
    )
    
    def validate_priority(self, value: str) -> str:
        """
        Validate the priority value.
        
        Args:
            value: The priority level to validate
            
        Returns:
            The validated priority level
        """
        valid_priorities = ['low', 'medium', 'urgent']
        if value not in valid_priorities:
            raise serializers.ValidationError(
                f"Priority must be one of: {', '.join(valid_priorities)}"
            )
        return value
    
    def validate_due_date(self, value: Any) -> Any:
        """
        Validate the due date.
        
        Args:
            value: The due date to validate
            
        Returns:
            The validated due date
        """
        # Could add date validation logic here
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> TaskModel:
        """
        Create a new work item with related entities.
        
        Args:
            validated_data: The validated data for the new work item
            
        Returns:
            The created work item instance
        """
        return super().create(validated_data)
    
    def update(self, instance: TaskModel, validated_data: Dict[str, Any]) -> TaskModel:
        """
        Update an existing work item with related entities.
        
        Args:
            instance: The existing work item to update
            validated_data: The validated data for updating
            
        Returns:
            The updated work item instance
        """
        return super().update(instance, validated_data)
    
    class Meta:
        """Configuration for the serializer."""
        model = TaskModel
        fields = [
            'id', 
            'title', 
            'description', 
            'due_date', 
            'priority', 
            'board_category', 
            'task_category', 
            'task_components', 
            'assigned_members', 
            'member_assignments'
        ]

# Aliases for backward compatibility with existing code
ContactSerializer = TeamMemberDataSerializer
BoardSerializer = ProjectWorkspaceSerializer
SubtaskSerializer = WorkItemComponentSerializer
TaskSerializer = WorkItemDataSerializer