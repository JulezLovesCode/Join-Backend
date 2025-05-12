# Join Backend - Django REST API

The backend server for the Join project management platform, providing a robust API for task and contact management.

## Overview

This is the server-side application for Join, which provides:

- RESTful API for task and contact management
- Email-based user authentication system
- Token-based authentication with guest access
- Comprehensive data model for tasks, subtasks, and contacts
- Performance metrics for the summary dashboard

## Directory Structure

```
join_server/
├── auth_module/      # User authentication
├── core_api/         # Task & contact management
├── server_config/    # Project settings
├── requirements.txt  # Dependencies
└── manage.py         # Django command utility
```

## Features

- **RESTful API:** Comprehensive endpoints for all application features
- **User Management:** Registration, authentication, and profile management
- **Task API:** Create, read, update, and delete tasks with filtering
- **Contact API:** Team member management with task assignments
- **Summary API:** Aggregated productivity metrics
- **Guest Mode:** Limited functionality without registration

## Technical Details

- Django REST Framework API
- Token-based authentication
- SQLite database (development) with PostgreSQL support
- Comprehensive data model for tasks, contacts, and users
- CORS handling for secure cross-origin requests

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Pip package manager

### Installation

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

5. Start the server:
   ```
   python manage.py runserver
   ```

The server will be available at `http://127.0.0.1:8000/`

## API Endpoints

- `/api/tasks/` - Task management
- `/api/subtasks/` - Subtask management
- `/api/contacts/` - Contact management
- `/api/auth/login/` - User authentication
- `/api/auth/registration/` - User registration
- `/api/auth/guest-login/` - Guest session creation
- `/api/summary/` - Performance metrics

## Development Notes

- Use the built-in Django admin at `/admin/` for data management
- API documentation is available at the root URL when in DEBUG mode
- Default database is SQLite, but can be configured for PostgreSQL
- CORS is enabled for localhost development by default
