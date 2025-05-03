"""
User Authentication Models Module

This module defines the extended user models used for authentication and 
user profile management. It includes a custom user model that uses email
as the primary identifier and an associated profile model for storing
additional user information.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class EmailBasedAuthenticationUser(AbstractUser):
    """
    Extended user model that uses email as the primary identifier.
    
    This model enhances Django's default user model by making email
    the primary means of authentication while maintaining compatibility
    with Django's authentication system.
    """
    
    # Override email field to ensure uniqueness
    email = models.EmailField(_('email address'), unique=True)
    
    # Authentication configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def configure_authorization_relationships(self):
        """
        Configure the authorization relationships for this user model.
        
        This method defines the relationship fields that connect users
        to Django's permission system, with custom related names to
        avoid conflicts with the default user model.
        
        Returns:
            dict: Field definitions for authorization relationships
        """
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
    
    # Apply the authorization relationship fields
    groups = configure_authorization_relationships.__get__(object)()['groups']
    user_permissions = configure_authorization_relationships.__get__(object)()['user_permissions']
    
    def get_full_name(self):
        """
        Return the full name of the user.
        
        Returns:
            str: The user's full name (first name + last name)
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email
    
    def get_short_name(self):
        """
        Return a short identifier for the user.
        
        Returns:
            str: The user's first name if available, otherwise username
        """
        return self.first_name if self.first_name else self.username
    
    def __str__(self):
        """
        Return a string representation of the user.
        
        Returns:
            str: The user's email address
        """
        return self.email


class ExtendedUserInformation(models.Model):
    """
    Extended profile information for users.
    
    This model stores additional information about users that is not
    part of the core authentication data, such as biography and location.
    """
    
    # Core relationship
    user = models.OneToOneField(
        EmailBasedAuthenticationUser, 
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        related_name='profile'
    )
    
    # Profile information fields
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
    
    # Metadata fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('creation date'),
        help_text=_('Date when the profile was created')
    )
    
    def get_display_name(self):
        """
        Return a human-readable identifier for this profile.
        
        Returns:
            str: The associated user's email address
        """
        return self.user.email
    
    def __str__(self):
        """
        Return a string representation of the profile.
        
        Returns:
            str: The associated user's email address
        """
        return self.get_display_name()


# Aliases for backward compatibility
CustomUser = EmailBasedAuthenticationUser
UserProfile = ExtendedUserInformation