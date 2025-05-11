from django.db import models
from django.utils.translation import gettext_lazy as _

class TaskStatusOptions:
    PENDING = 'to-do'
    IN_PROGRESS = 'in-progress'
    REVIEW = 'await-feedback'
    COMPLETED = 'done'
    
    @classmethod
    def getChoices(cls):
        return [
            (cls.PENDING, _('To Do')),
            (cls.IN_PROGRESS, _('In Progress')),
            (cls.REVIEW, _('Await Feedback')),
            (cls.COMPLETED, _('Done')),
        ]

class TaskPriorityOptions:
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'urgent'
    
    @classmethod
    def getChoices(cls):
        return [
            (cls.LOW, _('Low')),
            (cls.MEDIUM, _('Medium')),
            (cls.HIGH, _('Urgent')),
        ]

class TaskCategoryOptions:
    TECHNICAL = 'Technical Task'
    USER_STORY = 'User Story'
    
    @classmethod
    def getChoices(cls):
        return [
            (cls.TECHNICAL, _('Technical Task')),
            (cls.USER_STORY, _('User Story')),
        ]

class WorkItem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    
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
    
    contacts = models.ManyToManyField(
        "TeamMember", 
        related_name="assignments"
    )
    
    def getDisplayTitle(self):
        return self.title
    
    def __str__(self):
        return self.getDisplayTitle()

class WorkItemComponent(models.Model):
    parent_item = models.ForeignKey(
        "WorkItem", 
        on_delete=models.CASCADE, 
        related_name="components"
    )
    
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    
    def getDisplayTitle(self):
        return self.title
    
    def __str__(self):
        return self.getDisplayTitle()

class TeamMember(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    
    color = models.CharField(max_length=7, default='#000000')
    
    def getDisplayName(self):
        return self.name
    
    def __str__(self):
        return self.getDisplayName()

class ProjectSpace(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def getDisplayName(self):
        return self.name
    
    def __str__(self):
        return self.getDisplayName()

Task = WorkItem
Subtask = WorkItemComponent
Contact = TeamMember
Board = ProjectSpace