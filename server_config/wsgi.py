
import os
from django.core.wsgi import get_wsgi_application

def prepareWsgiEnvironment():
    """
    Configure necessary environment variables for WSGI operation.
    
    This function ensures Django uses the correct settings module
    when processing web requests in production and development environments.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_config.settings')

def createWsgiHandler():
    """
    Initialize and configure the WSGI application handler.
    
    This function sets up the environment and creates the WSGI application
    object that web servers will use to communicate with the Django application.
    
    Returns:
        The configured WSGI application handler ready for server integration.
    """
    # Ensure environment is properly configured before initializing
    prepareWsgiEnvironment()
    
    # Create and return the WSGI application handler
    return get_wsgi_application()

# The primary WSGI handler for use with web servers
wsgiHandler = createWsgiHandler()

# The entry point that WSGI servers will use (maintains backward compatibility)
application = wsgiHandler