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
    
    @staticmethod
    def generateTestData():
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
    
    def setUp(self):
        self.testConfig = ModelTestConfiguration()
        self.testData = self.testConfig.generateTestData()
        self.contactData = self.testData['contact']
        
        self.testContact = Contact.objects.create(**self.contactData)
    
    def testContactCreation(self):
        self.assertEqual(self.testContact.name, self.contactData['name'])
        self.assertEqual(self.testContact.email, self.contactData['email'])
        self.assertEqual(self.testContact.phone, self.contactData['phone'])
        self.assertEqual(self.testContact.color, self.contactData['color'])
    
    def testContactStrRepresentation(self):
        self.assertEqual(str(self.testContact), self.contactData['name'])
    
    def testContactEmailUniqueness(self):
        with self.assertRaises(Exception):
            Contact.objects.create(
                name='Another Contact',
                email=self.contactData['email'],
                phone='987-654-3210',
                color='#33FF57',
            )


class TaskModelTests(TestCase):
    
    def setUp(self):
        self.testConfig = ModelTestConfiguration()
        self.testData = self.testConfig.generateTestData()
        
        self.testContact = Contact.objects.create(**self.testData['contact'])
        
        self.taskData = self.testData['task']
        self.testTask = Task.objects.create(**self.taskData)
        
        self.testTask.contacts.add(self.testContact)
        
        self.subtaskData = self.testData['subtask']
        self.testSubtask = Subtask.objects.create(
            task=self.testTask,
            **self.subtaskData
        )
    
    def testTaskCreation(self):
        self.assertEqual(self.testTask.title, self.taskData['title'])
        self.assertEqual(self.testTask.description, self.taskData['description'])
        self.assertEqual(self.testTask.due_date, self.taskData['due_date'])
        self.assertEqual(self.testTask.priority, self.taskData['priority'])
        self.assertEqual(self.testTask.status, self.taskData['status'])
        self.assertEqual(self.testTask.task_category, self.taskData['task_category'])
    
    def testTaskContactRelationship(self):
        self.assertEqual(self.testTask.contacts.count(), 1)
        self.assertEqual(self.testTask.contacts.first(), self.testContact)
        
        self.assertEqual(self.testContact.tasks.count(), 1)
        self.assertEqual(self.testContact.tasks.first(), self.testTask)
    
    def testTaskSubtaskRelationship(self):
        self.assertEqual(self.testTask.subtasks.count(), 1)
        self.assertEqual(self.testTask.subtasks.first(), self.testSubtask)
    
    def testTaskDeletion(self):
        task_id = self.testTask.id
        subtask_id = self.testSubtask.id
        
        self.assertTrue(Task.objects.filter(id=task_id).exists())
        self.assertTrue(Subtask.objects.filter(id=subtask_id).exists())
        
        self.testTask.delete()
        
        self.assertFalse(Task.objects.filter(id=task_id).exists())
        self.assertFalse(Subtask.objects.filter(id=subtask_id).exists())


class SubtaskModelTests(TestCase):
    
    def setUp(self):
        self.testConfig = ModelTestConfiguration()
        self.testData = self.testConfig.generateTestData()
        
        self.testTask = Task.objects.create(**self.testData['task'])
        
        self.subtaskData = self.testData['subtask']
        self.testSubtask = Subtask.objects.create(
            task=self.testTask,
            **self.subtaskData
        )
    
    def testSubtaskCreation(self):
        self.assertEqual(self.testSubtask.title, self.subtaskData['title'])
        self.assertEqual(self.testSubtask.completed, self.subtaskData['completed'])
        self.assertEqual(self.testSubtask.task, self.testTask)
    
    def testSubtaskTaskRelationship(self):
        self.assertEqual(self.testSubtask.task, self.testTask)
        self.assertEqual(self.testTask.subtasks.count(), 1)
        self.assertEqual(self.testTask.subtasks.first(), self.testSubtask)
    
    def testSubtaskCompletion(self):
        self.assertFalse(self.testSubtask.completed)
        
        self.testSubtask.completed = True
        self.testSubtask.save()
        
        updated_subtask = Subtask.objects.get(id=self.testSubtask.id)
        self.assertTrue(updated_subtask.completed)


class BoardModelTests(TestCase):
    
    def setUp(self):
        self.testConfig = ModelTestConfiguration()
        self.testData = self.testConfig.generateTestData()
        
        self.boardData = self.testData['board']
        self.testBoard = Board.objects.create(**self.boardData)
    
    def testBoardCreation(self):
        self.assertEqual(self.testBoard.name, self.boardData['name'])
    
    def testBoardNameUniqueness(self):
        with self.assertRaises(Exception):
            Board.objects.create(name=self.boardData['name'])


class SerializerTestConfiguration:
    
    @staticmethod
    def generateSerializerTestData():
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
    
    def setUp(self):
        self.testConfig = SerializerTestConfiguration()
        self.testData = self.testConfig.generateSerializerTestData()
        self.contactData = self.testData['contact']
    
    def testContactSerialization(self):
        contact = Contact.objects.create(**self.contactData)
        serializer = ContactSerializer(contact)
        data = serializer.data
        
        self.assertEqual(data['name'], self.contactData['name'])
        self.assertEqual(data['email'], self.contactData['email'])
        self.assertEqual(data['phone'], self.contactData['phone'])
        self.assertEqual(data['color'], self.contactData['color'])
    
    def testContactDeserialization(self):
        serializer = ContactSerializer(data=self.contactData)
        self.assertTrue(serializer.is_valid())
        
        contact = serializer.save()
        self.assertEqual(contact.name, self.contactData['name'])
        self.assertEqual(contact.email, self.contactData['email'])
        self.assertEqual(contact.phone, self.contactData['phone'])
        self.assertEqual(contact.color, self.contactData['color'])
    
    def testInvalidContactData(self):
        invalid_data = self.contactData.copy()
        del invalid_data['email']
        
        serializer = ContactSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class TaskSerializerTests(APITestCase):
    
    def setUp(self):
        self.testConfig = SerializerTestConfiguration()
        self.testData = self.testConfig.generateSerializerTestData()
        
        self.contactData = self.testData['contact']
        self.testContact = Contact.objects.create(**self.contactData)
        
        self.taskData = self.testData['task']
        self.taskData['contact_ids'] = [self.testContact.id]
    
    def testTaskSerialization(self):
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
        serializer = TaskSerializer(data=self.taskData)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        task = serializer.save()
        self.assertEqual(task.title, self.taskData['title'])
        self.assertEqual(task.description, self.taskData['description'])
        self.assertEqual(task.priority, self.taskData['priority'])
        self.assertEqual(task.contacts.count(), 1)
        self.assertEqual(task.contacts.first(), self.testContact)


class IntegrationTestConfiguration:
    
    @staticmethod
    def createTestUser():
        return CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
    
    @staticmethod
    def generateIntegrationTestData():
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
    
    def setUp(self):
        self.testConfig = IntegrationTestConfiguration()
        self.testData = self.testConfig.generateIntegrationTestData()
        
        self.testUser = self.testConfig.createTestUser()
        self.client = APIClient()
        self.client.force_authenticate(user=self.testUser)
        
        self.contactData = self.testData['contact']
        self.testContact = Contact.objects.create(**self.contactData)
        
        self.taskData = self.testData['task']
        self.taskData['contact_ids'] = [self.testContact.id]
    
    def testTaskListEndpoint(self):
        Task.objects.create(**{k: v for k, v in self.taskData.items() if k != 'contact_ids'})
        
        url = reverse('task-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.taskData['title'])
    
    def testTaskCreateEndpoint(self):
        url = reverse('task-list')
        response = self.client.post(url, self.taskData, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.first().title, self.taskData['title'])
    
    def testTaskUpdateEndpoint(self):
        task = Task.objects.create(**{k: v for k, v in self.taskData.items() if k != 'contact_ids'})
        
        update_data = {
            'title': 'Updated Task Title',
            'priority': 'urgent',
            'contact_ids': [self.testContact.id],
        }
        
        url = reverse('task-detail', args=[task.id])
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        task.refresh_from_db()
        self.assertEqual(task.title, update_data['title'])
        self.assertEqual(task.priority, update_data['priority'])
    
    def testTaskDeleteEndpoint(self):
        task = Task.objects.create(**{k: v for k, v in self.taskData.items() if k != 'contact_ids'})
        
        url = reverse('task-detail', args=[task.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)
    
    def testUnauthenticatedAccess(self):
        self.client.force_authenticate(user=None)
        
        url = reverse('task-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.get(f"{url}?guest_id=test123")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestExecutionManager:
    
    @staticmethod
    def runModelTests():
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
        test_cases = [
            ContactSerializerTests,
            TaskSerializerTests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)
    
    @staticmethod
    def runIntegrationTests():
        test_cases = [
            TaskViewSetIntegrationTests,
        ]
        
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    import unittest
    import sys
    
    if len(sys.argv) > 1:
        if 'models' in sys.argv:
            TestExecutionManager.runModelTests()
        if 'serializers' in sys.argv:
            TestExecutionManager.runSerializerTests()
        if 'integration' in sys.argv:
            TestExecutionManager.runIntegrationTests()
    else:
        unittest.main()