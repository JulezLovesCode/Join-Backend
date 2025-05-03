"""
ASGI configuration for join_backend project.

This module defines the ASGI application entrypoint for asynchronous web servers.
It prepares the application interface for ASGI-compatible servers to communicate with the project.

Reference documentation:
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application

def configureAsgiEnvironment():
    """
    Set up the required environment variables for ASGI operation.
    
    This function ensures that Django knows which settings module to use
    when handling ASGI requests in various deployment environments.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_config.settings')

def initializeAsgiHandler():
    """
    Create and initialize the ASGI application handler.
    
    Returns:
        The configured ASGI application object ready for server integration.
    """
    configureAsgiEnvironment()
    return get_asgi_application()

# Initialize the ASGI application interface for web server integration
asgiHandler = initializeAsgiHandler()

# The entry point that ASGI servers will use to communicate with the application
application = asgiHandler