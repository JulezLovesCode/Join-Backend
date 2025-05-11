from django.shortcuts import render
from django.http import HttpResponse
from core_api.models import Task, Subtask, Contact, Board
from auth_module.models import EmailBasedAuthenticationUser
import json

def custom_admin_dashboard(request):
    """A simple custom admin dashboard with no authentication"""
    task_count = Task.objects.count()
    subtask_count = Subtask.objects.count()
    contact_count = Contact.objects.count()
    board_count = Board.objects.count()
    user_count = EmailBasedAuthenticationUser.objects.count()
    
    context = {
        'task_count': task_count,
        'subtask_count': subtask_count,
        'contact_count': contact_count,
        'board_count': board_count,
        'user_count': user_count,
    }
    
    return render(request, 'admin/dashboard.html', context)

def custom_admin_tasks(request):
    """View all tasks in JSON format"""
    tasks = list(Task.objects.values())
    return HttpResponse(json.dumps(tasks, indent=2, default=str), content_type="application/json")

def custom_admin_contacts(request):
    """View all contacts in JSON format"""
    contacts = list(Contact.objects.values())
    return HttpResponse(json.dumps(contacts, indent=2, default=str), content_type="application/json")

def custom_admin_users(request):
    """View all users in JSON format"""
    users = list(EmailBasedAuthenticationUser.objects.values('id', 'username', 'email', 'is_staff', 'is_superuser'))
    return HttpResponse(json.dumps(users, indent=2, default=str), content_type="application/json")

def custom_admin_boards(request):
    """View all boards in JSON format"""
    boards = list(Board.objects.values())
    return HttpResponse(json.dumps(boards, indent=2, default=str), content_type="application/json")

def custom_admin_subtasks(request):
    """View all subtasks in JSON format"""
    subtasks = list(Subtask.objects.values())
    return HttpResponse(json.dumps(subtasks, indent=2, default=str), content_type="application/json")