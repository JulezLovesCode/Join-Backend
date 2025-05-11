from rest_framework import serializers
from typing import Dict, List, Any, Optional

from core_api.models import (
    Task as TaskModel,
    Subtask as SubtaskModel,
    Contact as TeamMemberModel,
    Board as ProjectModel
)

class TeamMemberDataSerializer(serializers.ModelSerializer):
    
    def validate_email(self, value: str) -> str:
        return value
    
    class Meta:
        model = TeamMemberModel
        fields = '__all__'
        
        read_only_fields = ['id']

class ProjectWorkspaceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProjectModel
        fields = '__all__'

class WorkItemComponentSerializer(serializers.ModelSerializer):
    
    def validate_title(self, value: str) -> str:
        return value
    
    class Meta:
        model = SubtaskModel
        fields = '__all__'

class WorkItemDataSerializer(serializers.ModelSerializer):
    
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
        valid_priorities = ['low', 'medium', 'urgent']
        if value not in valid_priorities:
            raise serializers.ValidationError(
                f"Priority must be one of: {', '.join(valid_priorities)}"
            )
        return value
    
    def validate_due_date(self, value: Any) -> Any:
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> TaskModel:
        return super().create(validated_data)
    
    def update(self, instance: TaskModel, validated_data: Dict[str, Any]) -> TaskModel:
        return super().update(instance, validated_data)
    
    class Meta:
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

ContactSerializer = TeamMemberDataSerializer
BoardSerializer = ProjectWorkspaceSerializer
SubtaskSerializer = WorkItemComponentSerializer
TaskSerializer = WorkItemDataSerializer