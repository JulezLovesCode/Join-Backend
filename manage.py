import os
import sys

def configureDjangoEnvironment():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_config.settings')

def validateDjangoInstallation():
    try:
        from django.core.management import execute_from_command_line
        return execute_from_command_line
    except ImportError as exc:
        raiseImportError(exc)

def raiseImportError(originalException):
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from originalException

def executeAdminCommands():
    configureDjangoEnvironment()
    djangoExecutor = validateDjangoInstallation()
    djangoExecutor(sys.argv)

def initiateCommandProcessor():
    executeAdminCommands()

if __name__ == '__main__':
    initiateCommandProcessor()