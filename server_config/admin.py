from django.contrib.admin import AdminSite

class NoLoginAdminSite(AdminSite):
    """
    Admin site that doesn't require authentication and grants all permissions.
    """
    def has_permission(self, request):
        # Grant all permissions without checking
        return True

    def has_module_permission(self, request, obj=None):
        # Grant module permissions without checking
        return True

    def has_view_permission(self, request, obj=None):
        # Grant view permissions without checking
        return True

    def has_add_permission(self, request, obj=None):
        # Grant add permissions without checking
        return True

    def has_change_permission(self, request, obj=None):
        # Grant change permissions without checking
        return True

    def has_delete_permission(self, request, obj=None):
        # Grant delete permissions without checking
        return True

# Create a custom admin site instance
no_login_admin_site = NoLoginAdminSite(name='no_login_admin')

# Create a custom ModelAdmin that doesn't check permissions
from django.contrib import admin
from django.contrib.auth.models import Group
from auth_module.models import EmailBasedAuthenticationUser, ExtendedUserInformation
from core_api.models import Task, Subtask, Contact, Board

class NoPermissionCheckModelAdmin(admin.ModelAdmin):
    """
    ModelAdmin class that doesn't check for permissions
    """
    def has_module_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

# Register models with our custom admin site and custom model admin
no_login_admin_site.register(Group, NoPermissionCheckModelAdmin)
no_login_admin_site.register(EmailBasedAuthenticationUser, NoPermissionCheckModelAdmin)
no_login_admin_site.register(ExtendedUserInformation, NoPermissionCheckModelAdmin)
no_login_admin_site.register(Task, NoPermissionCheckModelAdmin)
no_login_admin_site.register(Subtask, NoPermissionCheckModelAdmin)
no_login_admin_site.register(Contact, NoPermissionCheckModelAdmin)
no_login_admin_site.register(Board, NoPermissionCheckModelAdmin)