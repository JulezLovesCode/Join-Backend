#!/usr/bin/env python
"""
Command-line utility for Django administrative operations.
This tool provides a command interface for managing Django projects.
"""
import os
import sys

def configureDjangoEnvironment():
    """
    Initialize Django settings module in environment variables.
    Sets up the appropriate configuration path for Django operation.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_config.settings')

def validateDjangoInstallation():
    """
    Ensure Django framework is properly installed and accessible.
    Raises appropriate error if Django cannot be imported.
    """
    try:
        from django.core.management import execute_from_command_line
        return execute_from_command_line
    except ImportError as exc:
        raiseImportError(exc)

def raiseImportError(originalException):
    """
    Raise a more descriptive import error with troubleshooting suggestions.
    
    Args:
        originalException: The original ImportError that was caught
    """
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from originalException

def executeAdminCommands():
    """
    Process Django administrative tasks via command line arguments.
    Handles command execution after environment setup.
    """
    configureDjangoEnvironment()
    djangoExecutor = validateDjangoInstallation()
    djangoExecutor(sys.argv)

def initiateCommandProcessor():
    """
    Entry point function that triggers the command processing.
    Called when script is run directly.
    """
    executeAdminCommands()

if __name__ == '__main__':
    initiateCommandProcessor()