import os
from django.core.asgi import get_asgi_application

def configureAsgiEnvironment():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_config.settings')

def initializeAsgiHandler():
    configureAsgiEnvironment()
    return get_asgi_application()

asgiHandler = initializeAsgiHandler()

application = asgiHandler