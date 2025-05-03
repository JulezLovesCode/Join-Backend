"""
User Authentication Views Module

This module provides view controllers for all authentication-related functionality,
including user registration, login, profile management, and account operations.
The views handle both HTML page rendering and API endpoints for authentication
operations, implementing security best practices and proper access control.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DetailView, ListView, TemplateView, View
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token

from .models import CustomUser, UserProfile
from .forms import UserRegistrationForm, UserProfileForm, PasswordChangeForm
from .serializers import UserSerializer, ProfileSerializer


class AuthenticationBaseView:
    """
    Base class for authentication views with common functionality.
    
    This class provides shared methods and properties used across
    different authentication view classes for consistent behavior.
    """
    
    @staticmethod
    def get_success_message(action_type):
        """
        Generate a standardized success message for authentication actions.
        
        Args:
            action_type: The type of authentication action performed
            
        Returns:
            str: Formatted success message
        """
        messages = {
            'registration': "Account successfully created. You are now logged in.",
            'login': "Successfully logged in.",
            'logout': "You have been logged out.",
            'profile_update': "Your profile has been updated.",
            'password_change': "Your password has been changed successfully.",
        }
        return messages.get(action_type, "Operation completed successfully.")


class UserRegistrationView(CreateView):
    """
    View for handling new user registration.
    
    This view displays the registration form, validates user input,
    and creates new user accounts with associated profiles.
    """
    template_name = 'authentication/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        """
        Process valid form data and create a new user account.
        
        This method creates the user account, logs the user in,
        and redirects to the profile page.
        
        Args:
            form: The validated form
            
        Returns:
            HttpResponse: Redirect to success URL
        """
        user = form.save()
        
        # Create associated profile
        UserProfile.objects.create(user=user)
        
        # Auto-login after registration
        login(self.request, user)
        
        messages.success(
            self.request, 
            AuthenticationBaseView.get_success_message('registration')
        )
        
        return HttpResponseRedirect(self.success_url)


class UserLoginView(View):
    """
    View for handling user login.
    
    This view displays the login form, authenticates credentials,
    and establishes user sessions on successful login.
    """
    template_name = 'authentication/login.html'
    
    def get(self, request):
        """
        Display the login form.
        
        Args:
            request: HTTP request
            
        Returns:
            HttpResponse: Rendered login page
        """
        # Redirect logged-in users
        if request.user.is_authenticated:
            return redirect('profile')
        
        return render(request, self.template_name, {})
    
    def post(self, request):
        """
        Process login form submission.
        
        This method validates credentials, logs the user in,
        and redirects to the appropriate destination.
        
        Args:
            request: HTTP request with form data
            
        Returns:
            HttpResponse: Redirect on success or error page
        """
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(
                request, 
                AuthenticationBaseView.get_success_message('login')
            )
            
            # Redirect to requested page or default
            next_page = request.GET.get('next', 'profile')
            return redirect(next_page)
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, self.template_name, {'email': email})


@method_decorator(login_required, name='dispatch')
class UserLogoutView(View):
    """
    View for handling user logout.
    
    This view terminates the user's session and redirects
    to the login page or homepage.
    """
    
    def get(self, request):
        """
        Process logout request.
        
        Args:
            request: HTTP request
            
        Returns:
            HttpResponse: Redirect to login page
        """
        logout(request)
        messages.info(
            request, 
            AuthenticationBaseView.get_success_message('logout')
        )
        return redirect('login')


@method_decorator(login_required, name='dispatch')
class UserProfileView(UpdateView):
    """
    View for displaying and updating user profiles.
    
    This view allows users to view and edit their profile information,
    including personal details and preferences.
    """
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'authentication/profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self, queryset=None):
        """
        Retrieve the profile for the current user.
        
        Returns:
            UserProfile: The current user's profile
        """
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_context_data(self, **kwargs):
        """
        Provide additional context data for the template.
        
        Returns:
            dict: Template context variables
        """
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
    def form_valid(self, form):
        """
        Process valid form data and update the profile.
        
        Args:
            form: The validated form
            
        Returns:
            HttpResponse: Redirect to success URL
        """
        messages.success(
            self.request, 
            AuthenticationBaseView.get_success_message('profile_update')
        )
        return super().form_valid(form)


class PasswordChangeView(LoginRequiredMixin, View):
    """
    View for changing user passwords.
    
    This view provides a form for users to change their password
    and validates the current password before making changes.
    """
    template_name = 'authentication/password_change.html'
    
    def get(self, request):
        """
        Display the password change form.
        
        Args:
            request: HTTP request
            
        Returns:
            HttpResponse: Rendered password change page
        """
        form = PasswordChangeForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """
        Process password change form submission.
        
        Args:
            request: HTTP request with form data
            
        Returns:
            HttpResponse: Redirect on success or error page
        """
        form = PasswordChangeForm(request.POST)
        
        if form.is_valid():
            # Check current password
            current_password = form.cleaned_data.get('current_password')
            user = authenticate(email=request.user.email, password=current_password)
            
            if user is not None:
                # Set new password
                new_password = form.cleaned_data.get('new_password')
                user.set_password(new_password)
                user.save()
                
                # Re-authenticate with new password
                login(request, user)
                
                messages.success(
                    request, 
                    AuthenticationBaseView.get_success_message('password_change')
                )
                return redirect('profile')
            else:
                form.add_error('current_password', 'Incorrect password')
        
        return render(request, self.template_name, {'form': form})


# API Views for authentication
class UserRegistrationAPIView(APIView):
    """
    API endpoint for user registration.
    
    This view handles registration requests through the API,
    creating new user accounts and returning authentication tokens.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Process API registration request.
        
        Args:
            request: HTTP request with registration data
            
        Returns:
            Response: API response with status and data
        """
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Generate authentication token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    """
    API endpoint for user login.
    
    This view authenticates users via the API and returns
    authentication tokens for subsequent API requests.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Process API login request.
        
        Args:
            request: HTTP request with login credentials
            
        Returns:
            Response: API response with token or error
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(email=email, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email
            })
        
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileAPIView(APIView):
    """
    API endpoint for user profile operations.
    
    This view handles retrieving and updating user profile data
    via the API, with authentication required.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Retrieve the user's profile data.
        
        Args:
            request: HTTP request
            
        Returns:
            Response: API response with profile data
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        
        return Response(serializer.data)
    
    def patch(self, request):
        """
        Update the user's profile data.
        
        Args:
            request: HTTP request with profile updates
            
        Returns:
            Response: API response with updated data
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Concrete view implementations for different authentication scenarios
user_registration = UserRegistrationView.as_view()
user_login = UserLoginView.as_view()
user_logout = UserLogoutView.as_view()
user_profile = UserProfileView.as_view()
password_change = PasswordChangeView.as_view()

# API view implementations
api_register = UserRegistrationAPIView.as_view()
api_login = UserLoginAPIView.as_view()
api_profile = UserProfileAPIView.as_view()