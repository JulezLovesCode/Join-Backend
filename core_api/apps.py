from django.apps import AppConfig


class CoreApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_api'
    verbose_name = 'API Service'