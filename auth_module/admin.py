from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import CustomUser as AuthenticationUser


class UserAuthenticationAdminConfiguration:
    
    def __init__(self):
        self.admin_site = admin.site
        self.user_admin_class = DjangoUserAdmin
    
    def register_authentication_models(self):
        self.register_user_model()
    
    def register_user_model(self):
        self.admin_site.register(AuthenticationUser, self.user_admin_class)


def configure_authentication_admin():
    admin_config = UserAuthenticationAdminConfiguration()
    admin_config.register_authentication_models()


configure_authentication_admin()