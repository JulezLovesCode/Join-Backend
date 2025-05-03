"""
Database models for the API application.

This module defines the data structures for tasks, activities, users, and organizational elements
used throughout the application. It establishes relationships between different entities
and provides methods for data representation.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

class TaskStatusOptions:
    """
    Defines the possible status options for tasks in the system.
    
    These status values represent the workflow stages a task can be in,
    from creation to completion.
    """
    PENDING = 'to-do'
    IN_PROGRESS = 'in-progress'
    REVIEW = 'await-feedback'
    COMPLETED = 'done'
    
    @classmethod
    def getChoices(cls):
        """
        Generate choices list for Django model fields.
        
        Returns:
            list: Tuples of (value, display_name) for use in model field choices
        """
        return [
            (cls.PENDING, _('To Do')),
            (cls.IN_PROGRESS, _('In Progress')),
            (cls.REVIEW, _('Await Feedback')),
            (cls.COMPLETED, _('Done')),
        ]

class TaskPriorityOptions:
    """
    Defines the possible priority levels for tasks.
    
    These values represent the urgency or importance of tasks
    for prioritization and resource allocation.
    """
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'urgent'
    
    @classmethod
    def getChoices(cls):
        """
        Generate choices list for Django model fields.
        
        Returns:
            list: Tuples of (value, display_name) for use in model field choices
        """
        return [
            (cls.LOW, _('Low')),
            (cls.MEDIUM, _('Medium')),
            (cls.HIGH, _('Urgent')),
        ]

class TaskCategoryOptions:
    """
    Defines the possible category types for tasks.
    
    These categories help organize tasks based on their purpose
    or the type of work they represent.
    """
    TECHNICAL = 'Technical Task'
    USER_STORY = 'User Story'
    
    @classmethod
    def getChoices(cls):
        """
        Generate choices list for Django model fields.
        
        Returns:
            list: Tuples of (value, display_name) for use in model field choices
        """
        return [
            (cls.TECHNICAL, _('Technical Task')),
            (cls.USER_STORY, _('User Story')),
        ]

class WorkItem(models.Model):
    """
    Represents a task or work item in the system.
    
    A work item contains all information about a piece of work to be done,
    including its description, due date, priority, and associated people.
    """
    # Meta information fields
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    
    # Classification fields
    priority = models.CharField(
        max_length=10, 
        choices=TaskPriorityOptions.getChoices()
    )
    status = models.CharField(
        max_length=20, 
        choices=TaskStatusOptions.getChoices(), 
        default=TaskStatusOptions.PENDING
    )
    task_category = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        choices=TaskCategoryOptions.getChoices()
    )
    
    # Organization fields
    board_category = models.CharField(
        max_length=20, 
        choices=TaskStatusOptions.getChoices(), 
        default=TaskStatusOptions.PENDING
    )
    icon = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        default="/static/default.svg"
    )
    
    # Relationships
    contacts = models.ManyToManyField(
        "TeamMember", 
        related_name="assignments"
    )
    
    def getDisplayTitle(self):
        """
        Get a human-readable representation of this work item.
        
        Returns:
            str: The title of the work item
        """
        return self.title
    
    def __str__(self):
        """
        String representation of the work item.
        
        Returns:
            str: The title of the work item
        """
        return self.getDisplayTitle()

class WorkItemComponent(models.Model):
    """
    Represents a component or subtask of a larger work item.
    
    Work item components are smaller, discrete pieces of work that
    make up a larger task. They can be individually completed.
    """
    # Relationships
    parent_item = models.ForeignKey(
        "WorkItem", 
        on_delete=models.CASCADE, 
        related_name="components"
    )
    
    # Meta information
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    
    def getDisplayTitle(self):
        """
        Get a human-readable representation of this component.
        
        Returns:
            str: The title of the component
        """
        return self.title
    
    def __str__(self):
        """
        String representation of the component.
        
        Returns:
            str: The title of the component
        """
        return self.getDisplayTitle()

class TeamMember(models.Model):
    """
    Represents a person who can be assigned to work items.
    
    Team members are users of the system who can create, be assigned to,
    or collaborate on work items.
    """
    # Personal information
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    
    # Display settings
    color = models.CharField(max_length=7, default='#000000')
    
    def getDisplayName(self):
        """
        Get a human-readable representation of this team member.
        
        Returns:
            str: The name of the team member
        """
        return self.name
    
    def __str__(self):
        """
        String representation of the team member.
        
        Returns:
            str: The name of the team member
        """
        return self.getDisplayName()

class ProjectSpace(models.Model):
    """
    Represents a workspace or board for organizing work items.
    
    Project spaces provide a way to group related work items
    together for organizational purposes.
    """
    # Identification
    name = models.CharField(max_length=255, unique=True)
    
    def getDisplayName(self):
        """
        Get a human-readable representation of this project space.
        
        Returns:
            str: The name of the project space
        """
        return self.name
    
    def __str__(self):
        """
        String representation of the project space.
        
        Returns:
            str: The name of the project space
        """
        return self.getDisplayName()

# Legacy model names for backward compatibility with existing code
Task = WorkItem
Subtask = WorkItemComponent
Contact = TeamMember
Board = ProjectSpace