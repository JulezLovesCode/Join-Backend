import os
from django.core.wsgi import get_wsgi_application

def prepareWsgiEnvironment():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_config.settings')

def createWsgiHandler():
    prepareWsgiEnvironment()
    
    return get_wsgi_application()

wsgiHandler = createWsgiHandler()

application = wsgiHandler