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
    
    @staticmethod
    def generate_test_credentials():
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
    
    def setUp(self):
        self.config = AuthenticationTestConfiguration()
        self.credentials = self.config.generate_test_credentials()
        self.User = get_user_model()
        
        self.test_user = self.User.objects.create_user(
            email=self.credentials['standard_user']['email'],
            username=self.credentials['standard_user']['username'],
            password=self.credentials['standard_user']['password'],
            first_name=self.credentials['standard_user']['first_name'],
            last_name=self.credentials['standard_user']['last_name'],
        )
    
    def test_user_creation(self):
        self.assertEqual(self.test_user.email, self.credentials['standard_user']['email'])
        self.assertEqual(self.test_user.username, self.credentials['standard_user']['username'])
        self.assertEqual(self.test_user.first_name, self.credentials['standard_user']['first_name'])
        self.assertEqual(self.test_user.last_name, self.credentials['standard_user']['last_name'])
        self.assertTrue(self.test_user.check_password(self.credentials['standard_user']['password']))
    
    def test_email_as_username(self):
        self.assertEqual(self.User.USERNAME_FIELD, 'email')
        self.assertIn('username', self.User.REQUIRED_FIELDS)
    
    def test_user_string_representation(self):
        self.assertEqual(str(self.test_user), self.credentials['standard_user']['email'])
    
    def test_user_profile_creation(self):
        profile = UserProfile.objects.filter(user=self.test_user).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.test_user)


class UserProfileTests(TestCase):
    
    def setUp(self):
        self.config = AuthenticationTestConfiguration()
        self.credentials = self.config.generate_test_credentials()
        self.User = get_user_model()
        
        self.test_user = self.User.objects.create_user(
            email=self.credentials['standard_user']['email'],
            username=self.credentials['standard_user']['username'],
            password=self.credentials['standard_user']['password'],
        )
        
        self.test_profile = UserProfile.objects.create(
            user=self.test_user,
            bio="This is a test biography",
            location="Test City, Test Country"
        )
    
    def test_profile_creation(self):
        self.assertEqual(self.test_profile.user, self.test_user)
        self.assertEqual(self.test_profile.bio, "This is a test biography")
        self.assertEqual(self.test_profile.location, "Test City, Test Country")
        self.assertIsNotNone(self.test_profile.created_at)
    
    def test_profile_string_representation(self):
        self.assertEqual(str(self.test_profile), self.test_user.email)
    
    def test_profile_user_relationship(self):
        profile_from_user = self.test_user.profile
        self.assertEqual(profile_from_user, self.test_profile)


class AuthenticationAPITests(APITestCase):
    
    def setUp(self):
        self.config = AuthenticationTestConfiguration()
        self.credentials = self.config.generate_test_credentials()
        self.User = get_user_model()
        
        self.test_user = self.User.objects.create_user(
            email=self.credentials['standard_user']['email'],
            username=self.credentials['standard_user']['username'],
            password=self.credentials['standard_user']['password'],
        )
        
        self.client = APIClient()
    
    def test_login_endpoint(self):
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
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newuserpassword123',
            'password2': 'newuserpassword123',
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        new_user = self.User.objects.filter(email='newuser@example.com').first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, 'newuser')


class AuthenticationIntegrationTests(TestCase):
    
    def setUp(self):
        self.config = AuthenticationTestConfiguration()
        self.credentials = self.config.generate_test_credentials()
        self.User = get_user_model()
        
        self.test_user = self.User.objects.create_user(
            email=self.credentials['standard_user']['email'],
            username=self.credentials['standard_user']['username'],
            password=self.credentials['standard_user']['password'],
        )
        
        self.client = Client()
    
    def test_login_page(self):
        url = reverse('login')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')
    
    def test_login_form_submission(self):
        url = reverse('login')
        data = {
            'email': self.credentials['standard_user']['email'],
            'password': self.credentials['standard_user']['password'],
        }
        
        response = self.client.post(url, data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
    
    def test_password_reset_flow(self):
        url = reverse('password_reset')
        data = {
            'email': self.credentials['standard_user']['email'],
        }
        
        response = self.client.post(url, data, follow=True)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.credentials['standard_user']['email'])
        
        email_body = mail.outbox[0].body
        token_start = email_body.find('/reset/') + 7
        token_end = email_body.find('/', token_start)
        uidb64 = email_body[token_start:token_end]
        
        token_start = token_end + 1
        token_end = email_body.find('/', token_start)
        token = email_body[token_start:token_end]
        
        url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        response = self.client.get(url, follow=True)
        
        url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': 'set-password'})
        data = {
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456',
        }
        
        response = self.client.post(url, data, follow=True)
        
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('newpassword456'))


class TestExecutionManager:
    
    @staticmethod
    def run_model_tests():
        test_cases = [
            UserModelTests,
            UserProfileTests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)
    
    @staticmethod
    def run_api_tests():
        test_cases = [
            AuthenticationAPITests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)
    
    @staticmethod
    def run_integration_tests():
        test_cases = [
            AuthenticationIntegrationTests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    import unittest
    import sys
    
    if len(sys.argv) > 1:
        if 'models' in sys.argv:
            TestExecutionManager.run_model_tests()
        if 'api' in sys.argv:
            TestExecutionManager.run_api_tests()
        if 'integration' in sys.argv:
            TestExecutionManager.run_integration_tests()
    else:
        unittest.main()