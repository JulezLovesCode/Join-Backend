"""
Authentication System Test Suite

This comprehensive testing module validates the authentication system components,
including user models, authentication processes, API endpoints, and form validation.
The test suite ensures that user registration, login, password management, and
permission checking function correctly across the application.
"""
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
import json
import uuid

from user_auth_app.models import UserProfile
from user_auth_app.forms import CustomUserCreationForm, CustomUserChangeForm


class AuthenticationTestConfiguration:
    """
    Configuration class for authentication testing.
    
    This class provides helper methods and test data configurations
    for use across different authentication test cases.
    """
    
    @staticmethod
    def generate_test_credentials():
        """
        Generate test user credentials for authentication testing.
        
        Returns:
            dict: Dictionary of test credentials
        """
        return {
            'standard_user': {
                'email': 'test@example.com',
                'username': 'testuser',
                'password': 'securepassword123',
                'first_name': 'Test',
                'last_name': 'User',
            },
            'admin_user': {
                'email': 'admin@example.com',
                'username': 'adminuser',
                'password': 'adminpassword456',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        }


class UserModelTests(TestCase):
    """
    Test cases for the custom user model functionality.
    
    These tests validate the behavior of the EmailBasedAuthenticationUser model,
    ensuring it correctly handles email-based authentication and user data.
    """
    
    def setUp(self):
        """
        Set up the test environment for user model tests.
        
        Creates test data and users to be used across test methods.
        """
        self.config = AuthenticationTestConfiguration()
        self.credentials = self.config.generate_test_credentials()
        self.User = get_user_model()
        
        # Create a test user
        self.test_user = self.User.objects.create_user(
            email=self.credentials['standard_user']['email'],
            username=self.credentials['standard_user']['username'],
            password=self.credentials['standard_user']['password'],
            first_name=self.credentials['standard_user']['first_name'],
            last_name=self.credentials['standard_user']['last_name'],
        )
    
    def test_user_creation(self):
        """Verify that a user can be created with expected attributes."""
        self.assertEqual(self.test_user.email, self.credentials['standard_user']['email'])
        self.assertEqual(self.test_user.username, self.credentials['standard_user']['username'])
        self.assertEqual(self.test_user.first_name, self.credentials['standard_user']['first_name'])
        self.assertEqual(self.test_user.last_name, self.credentials['standard_user']['last_name'])
        self.assertTrue(self.test_user.check_password(self.credentials['standard_user']['password']))
    
    def test_email_as_username(self):
        """Verify that email is used as the username field for authentication."""
        self.assertEqual(self.User.USERNAME_FIELD, 'email')
        self.assertIn('username', self.User.REQUIRED_FIELDS)
    
    def test_user_string_representation(self):
        """Verify the string representation of a user is their email."""
        self.assertEqual(str(self.test_user), self.credentials['standard_user']['email'])
    
    def test_user_profile_creation(self):
        """Verify that a user profile is created for a new user."""
        # Check that a profile exists for the test user
        profile = UserProfile.objects.filter(user=self.test_user).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.test_user)


class UserProfileTests(TestCase):
    """
    Test cases for the user profile functionality.
    
    These tests validate the behavior of the ExtendedUserInformation model,
    ensuring it correctly stores and manages additional user profile data.
    """
    
    def setUp(self):
        """
        Set up the test environment for user profile tests.
        
        Creates test users and profiles to be used across test methods.
        """
        self.config = AuthenticationTestConfiguration()
        self.credentials = self.config.generate_test_credentials()
        self.User = get_user_model()
        
        # Create a test user
        self.test_user = self.User.objects.create_user(
            email=self.credentials['standard_user']['email'],
            username=self.credentials['standard_user']['username'],
            password=self.credentials['standard_user']['password'],
        )
        
        # Create a profile for the test user
        self.test_profile = UserProfile.objects.create(
            user=self.test_user,
            bio="This is a test biography",
            location="Test City, Test Country"
        )
    
    def test_profile_creation(self):
        """Verify that a profile can be created with expected attributes."""
        self.assertEqual(self.test_profile.user, self.test_user)
        self.assertEqual(self.test_profile.bio, "This is a test biography")
        self.assertEqual(self.test_profile.location, "Test City, Test Country")
        self.assertIsNotNone(self.test_profile.created_at)
    
    def test_profile_string_representation(self):
        """Verify the string representation of a profile is the user's email."""
        self.assertEqual(str(self.test_profile), self.test_user.email)
    
    def test_profile_user_relationship(self):
        """Verify the one-to-one relationship between user and profile."""
        # Retrieve the profile through the user relationship
        profile_from_user = self.test_user.profile
        self.assertEqual(profile_from_user, self.test_profile)


class AuthenticationAPITests(APITestCase):
    """
    Test cases for the authentication API endpoints.
    
    These tests validate the behavior of the REST API endpoints related to
    authentication, including login, registration, and token operations.
    """
    
    def setUp(self):
        """
        Set up the test environment for API tests.
        
        Creates test data and clients to be used across test methods.
        """
        self.config = AuthenticationTestConfiguration()
        self.credentials = self.config.generate_test_credentials()
        self.User = get_user_model()
        
        # Create a test user
        self.test_user = self.User.objects.create_user(
            email=self.credentials['standard_user']['email'],
            username=self.credentials['standard_user']['username'],
            password=self.credentials['standard_user']['password'],
        )
        
        # Create an API client
        self.client = APIClient()
    
    def test_login_endpoint(self):
        """Verify that the login endpoint correctly authenticates users."""
        url = reverse('token_obtain_pair')
        data = {
            'email': self.credentials['standard_user']['email'],
            'password': self.credentials['standard_user']['password'],
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_register_endpoint(self):
        """Verify that the registration endpoint correctly creates new users."""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newuserpassword123',
            'password2': 'newuserpassword123',  # Confirmation password
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the user was created
        new_user = self.User.objects.filter(email='newuser@example.com').first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, 'newuser')


class AuthenticationIntegrationTests(TestCase):
    """
    Integration tests for the authentication system.
    
    These tests validate the behavior of the authentication system as a whole,
    including view rendering, form submission, and session management.
    """
    
    def setUp(self):
        """
        Set up the test environment for integration tests.
        
        Creates test data and clients to be used across test methods.
        """
        self.config = AuthenticationTestConfiguration()
        self.credentials = self.config.generate_test_credentials()
        self.User = get_user_model()
        
        # Create a test user
        self.test_user = self.User.objects.create_user(
            email=self.credentials['standard_user']['email'],
            username=self.credentials['standard_user']['username'],
            password=self.credentials['standard_user']['password'],
        )
        
        # Create a test client
        self.client = Client()
    
    def test_login_page(self):
        """Verify that the login page renders correctly."""
        url = reverse('login')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')
    
    def test_login_form_submission(self):
        """Verify that the login form correctly authenticates users."""
        url = reverse('login')
        data = {
            'email': self.credentials['standard_user']['email'],
            'password': self.credentials['standard_user']['password'],
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Check that the user is logged in
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
    
    def test_password_reset_flow(self):
        """Verify the password reset flow functions correctly."""
        # Request password reset
        url = reverse('password_reset')
        data = {
            'email': self.credentials['standard_user']['email'],
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.credentials['standard_user']['email'])
        
        # Extract the reset token and uidb64 from the email
        email_body = mail.outbox[0].body
        token_start = email_body.find('/reset/') + 7
        token_end = email_body.find('/', token_start)
        uidb64 = email_body[token_start:token_end]
        
        token_start = token_end + 1
        token_end = email_body.find('/', token_start)
        token = email_body[token_start:token_end]
        
        # Use the token to reset the password
        url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        response = self.client.get(url, follow=True)
        
        # Set new password
        url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': 'set-password'})
        data = {
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456',
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Verify the password was changed
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('newpassword456'))


class TestExecutionManager:
    """
    Test execution manager to organize and run test suites.
    
    This class provides a structured way to organize and execute
    related test cases as a unified test suite.
    """
    
    @staticmethod
    def run_model_tests():
        """Run all model-related test cases."""
        test_cases = [
            UserModelTests,
            UserProfileTests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)
    
    @staticmethod
    def run_api_tests():
        """Run all API-related test cases."""
        test_cases = [
            AuthenticationAPITests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)
    
    @staticmethod
    def run_integration_tests():
        """Run all integration test cases."""
        test_cases = [
            AuthenticationIntegrationTests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)

# Enable direct execution of specific test suites
if __name__ == '__main__':
    import unittest
    import sys
    
    # Parse command line arguments for specific test suites
    if len(sys.argv) > 1:
        if 'models' in sys.argv:
            TestExecutionManager.run_model_tests()
        if 'api' in sys.argv:
            TestExecutionManager.run_api_tests()
        if 'integration' in sys.argv:
            TestExecutionManager.run_integration_tests()
    else:
        # Run all tests by default
        unittest.main()