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
# Import forms and serializers
try:
    from .forms import UserRegistrationForm, UserProfileForm, PasswordChangeForm
except ImportError:
    # During development/setup, provide dummy classes to avoid errors
    from django import forms
    class UserRegistrationForm(forms.Form): pass
    class UserProfileForm(forms.Form): pass
    class PasswordChangeForm(forms.Form): pass

try:
    from .serializers import UserSerializer, ProfileSerializer
except ImportError:
    # During development/setup, provide dummy classes to avoid errors
    from rest_framework import serializers
    class UserSerializer(serializers.Serializer): pass
    class ProfileSerializer(serializers.Serializer): pass


class AuthenticationBaseView:
    @staticmethod
    def get_success_message(action_type):
        messages = {
            'registration': "Account successfully created. You are now logged in.",
            'login': "Successfully logged in.",
            'logout': "You have been logged out.",
            'profile_update': "Your profile has been updated.",
            'password_change': "Your password has been changed successfully.",
        }
        return messages.get(action_type, "Operation completed successfully.")


class UserRegistrationView(CreateView):
    template_name = 'authentication/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        user = form.save()
        
        UserProfile.objects.create(user=user)
        
        login(self.request, user)
        
        messages.success(
            self.request, 
            AuthenticationBaseView.get_success_message('registration')
        )
        
        return HttpResponseRedirect(self.success_url)


class UserLoginView(View):
    template_name = 'authentication/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('profile')
        
        return render(request, self.template_name, {})
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(
                request, 
                AuthenticationBaseView.get_success_message('login')
            )
            
            next_page = request.GET.get('next', 'profile')
            return redirect(next_page)
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, self.template_name, {'email': email})


@method_decorator(login_required, name='dispatch')
class UserLogoutView(View):
    
    def get(self, request):
        logout(request)
        messages.info(
            request, 
            AuthenticationBaseView.get_success_message('logout')
        )
        return redirect('login')


@method_decorator(login_required, name='dispatch')
class UserProfileView(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'authentication/profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self, queryset=None):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            AuthenticationBaseView.get_success_message('profile_update')
        )
        return super().form_valid(form)


class PasswordChangeView(LoginRequiredMixin, View):
    template_name = 'authentication/password_change.html'
    
    def get(self, request):
        form = PasswordChangeForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PasswordChangeForm(request.POST)
        
        if form.is_valid():
            current_password = form.cleaned_data.get('current_password')
            user = authenticate(email=request.user.email, password=current_password)
            
            if user is not None:
                new_password = form.cleaned_data.get('new_password')
                user.set_password(new_password)
                user.save()
                
                login(request, user)
                
                messages.success(
                    request, 
                    AuthenticationBaseView.get_success_message('password_change')
                )
                return redirect('profile')
            else:
                form.add_error('current_password', 'Incorrect password')
        
        return render(request, self.template_name, {'form': form})


class UserRegistrationAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            UserProfile.objects.create(user=user)
            
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
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
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        
        return Response(serializer.data)
    
    def patch(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


user_registration = UserRegistrationView.as_view()
user_login = UserLoginView.as_view()
user_logout = UserLogoutView.as_view()
user_profile = UserProfileView.as_view()
password_change = PasswordChangeView.as_view()

api_register = UserRegistrationAPIView.as_view()
api_login = UserLoginAPIView.as_view()
api_profile = UserProfileAPIView.as_view()