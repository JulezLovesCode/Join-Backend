"""
Comprehensive Test Suite for API Functionality

This module contains test cases for the API application, covering models,
serializers, views, and integration points. The test suite is designed
to validate core application behavior and ensure reliability of the API.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework import status
from datetime import datetime, timedelta
import json
import uuid

from api.models import Task, Subtask, Contact, Board
from api.serializers import TaskSerializer, SubtaskSerializer, ContactSerializer
from user_auth_app.models import CustomUser

class ModelTestConfiguration:
    """
    Configuration class for model test data.
    
    This class provides helper methods and test data configurations
    for use across different test cases.
    """
    
    @staticmethod
    def generateTestData():
        """
        Generate test data for model testing.
        
        Returns:
            dict: Dictionary of test data for different models
        """
        return {
            'contact': {
                'name': 'Test Contact',
                'email': 'test@example.com',
                'phone': '123-456-7890',
                'color': '#FF5733',
            },
            'task': {
                'title': 'Test Task',
                'description': 'This is a test task description',
                'due_date': timezone.now().date() + timedelta(days=7),
                'priority': 'medium',
                'status': 'to-do',
                'task_category': 'Technical Task',
                'board_category': 'to-do',
            },
            'subtask': {
                'title': 'Test Subtask',
                'completed': False,
            },
            'board': {
                'name': 'Test Board',
            }
        }


class ContactModelTests(TestCase):
    """
    Test cases for the Contact model functionality.
    
    These tests validate the behavior of the Contact model,
    ensuring it correctly stores and retrieves contact information.
    """
    
    def setUp(self):
        """
        Set up the test environment for Contact tests.
        
        Creates test data to be used across test methods.
        """
        self.testConfig = ModelTestConfiguration()
        self.testData = self.testConfig.generateTestData()
        self.contactData = self.testData['contact']
        
        # Create a test contact for use in tests
        self.testContact = Contact.objects.create(**self.contactData)
    
    def testContactCreation(self):
        """Verify that a contact can be created with the expected attributes."""
        self.assertEqual(self.testContact.name, self.contactData['name'])
        self.assertEqual(self.testContact.email, self.contactData['email'])
        self.assertEqual(self.testContact.phone, self.contactData['phone'])
        self.assertEqual(self.testContact.color, self.contactData['color'])
    
    def testContactStrRepresentation(self):
        """Verify the string representation of a contact matches its name."""
        self.assertEqual(str(self.testContact), self.contactData['name'])
    
    def testContactEmailUniqueness(self):
        """Verify that contacts must have unique email addresses."""
        # Try to create a second contact with the same email
        with self.assertRaises(Exception):
            Contact.objects.create(
                name='Another Contact',
                email=self.contactData['email'],  # Same email as existing contact
                phone='987-654-3210',
                color='#33FF57',
            )


class TaskModelTests(TestCase):
    """
    Test cases for the Task model functionality.
    
    These tests validate the behavior of the Task model,
    ensuring it correctly manages task information and relationships.
    """
    
    def setUp(self):
        """
        Set up the test environment for Task tests.
        
        Creates test data and relationships for use across test methods.
        """
        self.testConfig = ModelTestConfiguration()
        self.testData = self.testConfig.generateTestData()
        
        # Create a contact for task assignment
        self.testContact = Contact.objects.create(**self.testData['contact'])
        
        # Create a task with basic information
        self.taskData = self.testData['task']
        self.testTask = Task.objects.create(**self.taskData)
        
        # Associate the contact with the task
        self.testTask.contacts.add(self.testContact)
        
        # Create a subtask associated with the task
        self.subtaskData = self.testData['subtask']
        self.testSubtask = Subtask.objects.create(
            task=self.testTask,
            **self.subtaskData
        )
    
    def testTaskCreation(self):
        """Verify that a task can be created with the expected attributes."""
        self.assertEqual(self.testTask.title, self.taskData['title'])
        self.assertEqual(self.testTask.description, self.taskData['description'])
        self.assertEqual(self.testTask.due_date, self.taskData['due_date'])
        self.assertEqual(self.testTask.priority, self.taskData['priority'])
        self.assertEqual(self.testTask.status, self.taskData['status'])
        self.assertEqual(self.testTask.task_category, self.taskData['task_category'])
    
    def testTaskContactRelationship(self):
        """Verify the relationship between tasks and contacts."""
        self.assertEqual(self.testTask.contacts.count(), 1)
        self.assertEqual(self.testTask.contacts.first(), self.testContact)
        
        # Test the reverse relationship
        self.assertEqual(self.testContact.tasks.count(), 1)
        self.assertEqual(self.testContact.tasks.first(), self.testTask)
    
    def testTaskSubtaskRelationship(self):
        """Verify the relationship between tasks and subtasks."""
        self.assertEqual(self.testTask.subtasks.count(), 1)
        self.assertEqual(self.testTask.subtasks.first(), self.testSubtask)
    
    def testTaskDeletion(self):
        """Verify that deleting a task also deletes its subtasks (cascade)."""
        task_id = self.testTask.id
        subtask_id = self.testSubtask.id
        
        # Verify objects exist
        self.assertTrue(Task.objects.filter(id=task_id).exists())
        self.assertTrue(Subtask.objects.filter(id=subtask_id).exists())
        
        # Delete the task
        self.testTask.delete()
        
        # Verify cascade deletion
        self.assertFalse(Task.objects.filter(id=task_id).exists())
        self.assertFalse(Subtask.objects.filter(id=subtask_id).exists())


class SubtaskModelTests(TestCase):
    """
    Test cases for the Subtask model functionality.
    
    These tests validate the behavior of the Subtask model,
    ensuring it correctly manages subtask information and relationships.
    """
    
    def setUp(self):
        """
        Set up the test environment for Subtask tests.
        
        Creates test data and relationships for use across test methods.
        """
        self.testConfig = ModelTestConfiguration()
        self.testData = self.testConfig.generateTestData()
        
        # Create a task for subtask association
        self.testTask = Task.objects.create(**self.testData['task'])
        
        # Create a subtask associated with the task
        self.subtaskData = self.testData['subtask']
        self.testSubtask = Subtask.objects.create(
            task=self.testTask,
            **self.subtaskData
        )
    
    def testSubtaskCreation(self):
        """Verify that a subtask can be created with the expected attributes."""
        self.assertEqual(self.testSubtask.title, self.subtaskData['title'])
        self.assertEqual(self.testSubtask.completed, self.subtaskData['completed'])
        self.assertEqual(self.testSubtask.task, self.testTask)
    
    def testSubtaskTaskRelationship(self):
        """Verify the relationship between subtasks and their parent tasks."""
        self.assertEqual(self.testSubtask.task, self.testTask)
        self.assertEqual(self.testTask.subtasks.count(), 1)
        self.assertEqual(self.testTask.subtasks.first(), self.testSubtask)
    
    def testSubtaskCompletion(self):
        """Verify subtask completion status can be updated."""
        self.assertFalse(self.testSubtask.completed)
        
        # Update completion status
        self.testSubtask.completed = True
        self.testSubtask.save()
        
        # Verify status change
        updated_subtask = Subtask.objects.get(id=self.testSubtask.id)
        self.assertTrue(updated_subtask.completed)


class BoardModelTests(TestCase):
    """
    Test cases for the Board model functionality.
    
    These tests validate the behavior of the Board model,
    ensuring it correctly manages board information.
    """
    
    def setUp(self):
        """
        Set up the test environment for Board tests.
        
        Creates test data for use across test methods.
        """
        self.testConfig = ModelTestConfiguration()
        self.testData = self.testConfig.generateTestData()
        
        # Create a board
        self.boardData = self.testData['board']
        self.testBoard = Board.objects.create(**self.boardData)
    
    def testBoardCreation(self):
        """Verify that a board can be created with the expected attributes."""
        self.assertEqual(self.testBoard.name, self.boardData['name'])
    
    def testBoardNameUniqueness(self):
        """Verify that boards must have unique names."""
        # Try to create a second board with the same name
        with self.assertRaises(Exception):
            Board.objects.create(name=self.boardData['name'])


class SerializerTestConfiguration:
    """
    Configuration class for serializer test data.
    
    This class provides helper methods and test data configurations
    for serializer testing.
    """
    
    @staticmethod
    def generateSerializerTestData():
        """
        Generate test data for serializer testing.
        
        Returns:
            dict: Dictionary of test data for different serializers
        """
        return {
            'contact': {
                'name': 'Serializer Contact',
                'email': 'serializer@example.com',
                'phone': '123-456-7890',
                'color': '#FF5733',
            },
            'task': {
                'title': 'Serializer Task',
                'description': 'This is a serializer test task',
                'due_date': (timezone.now() + timedelta(days=7)).date().isoformat(),
                'priority': 'medium',
                'board_category': 'to-do',
                'task_category': 'Technical Task',
            },
            'subtask': {
                'title': 'Serializer Subtask',
                'completed': False,
            },
        }


class ContactSerializerTests(TestCase):
    """
    Test cases for the Contact serializer functionality.
    
    These tests validate the behavior of the Contact serializer,
    ensuring it correctly converts between model instances and JSON data.
    """
    
    def setUp(self):
        """
        Set up the test environment for Contact serializer tests.
        
        Creates test data for use across test methods.
        """
        self.testConfig = SerializerTestConfiguration()
        self.testData = self.testConfig.generateSerializerTestData()
        self.contactData = self.testData['contact']
    
    def testContactSerialization(self):
        """Verify contact model instances are correctly serialized to JSON."""
        contact = Contact.objects.create(**self.contactData)
        serializer = ContactSerializer(contact)
        data = serializer.data
        
        self.assertEqual(data['name'], self.contactData['name'])
        self.assertEqual(data['email'], self.contactData['email'])
        self.assertEqual(data['phone'], self.contactData['phone'])
        self.assertEqual(data['color'], self.contactData['color'])
    
    def testContactDeserialization(self):
        """Verify JSON data is correctly deserialized to contact model instances."""
        serializer = ContactSerializer(data=self.contactData)
        self.assertTrue(serializer.is_valid())
        
        contact = serializer.save()
        self.assertEqual(contact.name, self.contactData['name'])
        self.assertEqual(contact.email, self.contactData['email'])
        self.assertEqual(contact.phone, self.contactData['phone'])
        self.assertEqual(contact.color, self.contactData['color'])
    
    def testInvalidContactData(self):
        """Verify invalid data is correctly rejected by the serializer."""
        # Missing required field
        invalid_data = self.contactData.copy()
        del invalid_data['email']
        
        serializer = ContactSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class TaskSerializerTests(APITestCase):
    """
    Test cases for the Task serializer functionality.
    
    These tests validate the behavior of the Task serializer,
    ensuring it correctly handles complex task data with relationships.
    """
    
    def setUp(self):
        """
        Set up the test environment for Task serializer tests.
        
        Creates test data and relationships for use across test methods.
        """
        self.testConfig = SerializerTestConfiguration()
        self.testData = self.testConfig.generateSerializerTestData()
        
        # Create a contact for task assignment
        self.contactData = self.testData['contact']
        self.testContact = Contact.objects.create(**self.contactData)
        
        # Prepare task data with contact assignment
        self.taskData = self.testData['task']
        self.taskData['contact_ids'] = [self.testContact.id]
    
    def testTaskSerialization(self):
        """Verify task model instances with relationships are correctly serialized."""
        task = Task.objects.create(**{k: v for k, v in self.taskData.items() if k != 'contact_ids'})
        task.contacts.add(self.testContact)
        
        serializer = TaskSerializer(task)
        data = serializer.data
        
        self.assertEqual(data['title'], self.taskData['title'])
        self.assertEqual(data['description'], self.taskData['description'])
        self.assertEqual(data['priority'], self.taskData['priority'])
        self.assertEqual(len(data['contacts']), 1)
        self.assertEqual(data['contacts'][0]['name'], self.contactData['name'])
    
    def testTaskDeserialization(self):
        """Verify JSON data with relationships is correctly deserialized to task instances."""
        serializer = TaskSerializer(data=self.taskData)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        task = serializer.save()
        self.assertEqual(task.title, self.taskData['title'])
        self.assertEqual(task.description, self.taskData['description'])
        self.assertEqual(task.priority, self.taskData['priority'])
        self.assertEqual(task.contacts.count(), 1)
        self.assertEqual(task.contacts.first(), self.testContact)


class IntegrationTestConfiguration:
    """
    Configuration class for API integration test data.
    
    This class provides helper methods and test data configurations
    for integration testing of the API endpoints.
    """
    
    @staticmethod
    def createTestUser():
        """
        Create a test user for authenticated API testing.
        
        Returns:
            CustomUser: A test user instance
        """
        return CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
    
    @staticmethod
    def generateIntegrationTestData():
        """
        Generate test data for API integration testing.
        
        Returns:
            dict: Dictionary of test data for API endpoints
        """
        return {
            'contact': {
                'name': 'API Contact',
                'email': f'api-{uuid.uuid4()}@example.com',
                'phone': '123-456-7890',
                'color': '#FF5733',
            },
            'task': {
                'title': 'API Task',
                'description': 'This is an API test task',
                'due_date': (timezone.now() + timedelta(days=7)).date().isoformat(),
                'priority': 'medium',
                'board_category': 'to-do',
                'task_category': 'Technical Task',
            },
        }


class TaskViewSetIntegrationTests(APITestCase):
    """
    Integration tests for the Task API endpoints.
    
    These tests validate the behavior of the Task API endpoints,
    ensuring they correctly handle CRUD operations and permissions.
    """
    
    def setUp(self):
        """
        Set up the test environment for Task API tests.
        
        Creates test data, users, and authenticates requests for testing.
        """
        self.testConfig = IntegrationTestConfiguration()
        self.testData = self.testConfig.generateIntegrationTestData()
        
        # Create a test user and authenticate
        self.testUser = self.testConfig.createTestUser()
        self.client = APIClient()
        self.client.force_authenticate(user=self.testUser)
        
        # Create a contact for task assignment
        self.contactData = self.testData['contact']
        self.testContact = Contact.objects.create(**self.contactData)
        
        # Prepare task data with contact assignment
        self.taskData = self.testData['task']
        self.taskData['contact_ids'] = [self.testContact.id]
    
    def testTaskListEndpoint(self):
        """Verify the task list endpoint returns expected data."""
        # Create a task to retrieve
        Task.objects.create(**{k: v for k, v in self.taskData.items() if k != 'contact_ids'})
        
        # Test the endpoint
        url = reverse('task-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.taskData['title'])
    
    def testTaskCreateEndpoint(self):
        """Verify the task create endpoint correctly creates tasks."""
        url = reverse('task-list')
        response = self.client.post(url, self.taskData, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.first().title, self.taskData['title'])
    
    def testTaskUpdateEndpoint(self):
        """Verify the task update endpoint correctly updates tasks."""
        # Create a task to update
        task = Task.objects.create(**{k: v for k, v in self.taskData.items() if k != 'contact_ids'})
        
        # Update data
        update_data = {
            'title': 'Updated Task Title',
            'priority': 'urgent',
            'contact_ids': [self.testContact.id],
        }
        
        url = reverse('task-detail', args=[task.id])
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify updates
        task.refresh_from_db()
        self.assertEqual(task.title, update_data['title'])
        self.assertEqual(task.priority, update_data['priority'])
    
    def testTaskDeleteEndpoint(self):
        """Verify the task delete endpoint correctly deletes tasks."""
        # Create a task to delete
        task = Task.objects.create(**{k: v for k, v in self.taskData.items() if k != 'contact_ids'})
        
        url = reverse('task-detail', args=[task.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)
    
    def testUnauthenticatedAccess(self):
        """Verify unauthenticated requests are properly handled."""
        # Log out the user
        self.client.force_authenticate(user=None)
        
        url = reverse('task-list')
        response = self.client.get(url)
        
        # Should require authentication or guest ID
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try with guest ID
        response = self.client.get(f"{url}?guest_id=test123")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestExecutionManager:
    """
    Test execution manager to organize and run test suites.
    
    This class provides a structured way to organize and group
    related test cases for execution.
    """
    
    @staticmethod
    def runModelTests():
        """Run all model-related test cases."""
        test_cases = [
            ContactModelTests,
            TaskModelTests,
            SubtaskModelTests,
            BoardModelTests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)
    
    @staticmethod
    def runSerializerTests():
        """Run all serializer-related test cases."""
        test_cases = [
            ContactSerializerTests,
            TaskSerializerTests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)
    
    @staticmethod
    def runIntegrationTests():
        """Run all integration test cases."""
        test_cases = [
            TaskViewSetIntegrationTests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)

# Enable direct execution of test suites
if __name__ == '__main__':
    import unittest
    import sys
    
    # Parse command line arguments for specific test suites
    if len(sys.argv) > 1:
        if 'models' in sys.argv:
            TestExecutionManager.runModelTests()
        if 'serializers' in sys.argv:
            TestExecutionManager.runSerializerTests()
        if 'integration' in sys.argv:
            TestExecutionManager.runIntegrationTests()
    else:
        # Run all tests by default
        unittest.main()