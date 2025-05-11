from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class EmailBasedAuthenticationUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def configure_authorization_relationships(self):
        return {
            'groups': models.ManyToManyField(
                "auth.Group",
                verbose_name=_('groups'),
                blank=True,
                related_name="customuser_set",
                help_text=_(
                    'The groups this user belongs to. A user will get all permissions '
                    'granted to each of their groups.'
                ),
            ),
            'user_permissions': models.ManyToManyField(
                "auth.Permission",
                verbose_name=_('user permissions'),
                blank=True,
                related_name="customuser_permissions_set",
                help_text=_('Specific permissions for this user.'),
            ),
        }
    
    groups = configure_authorization_relationships.__get__(object)()['groups']
    user_permissions = configure_authorization_relationships.__get__(object)()['user_permissions']
    
    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email
    
    def get_short_name(self):
        return self.first_name if self.first_name else self.username
    
    def __str__(self):
        return self.email


class ExtendedUserInformation(models.Model):
    user = models.OneToOneField(
        EmailBasedAuthenticationUser, 
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        related_name='profile'
    )
    
    bio = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('biography'),
        help_text=_('A short description about the user')
    )
    
    location = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name=_('location'),
        help_text=_('User\'s geographic location')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('creation date'),
        help_text=_('Date when the profile was created')
    )
    
    def get_display_name(self):
        return self.user.email
    
    def __str__(self):
        return self.get_display_name()


CustomUser = EmailBasedAuthenticationUser
UserProfile = ExtendedUserInformation