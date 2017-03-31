from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client

class LogoutTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create_user(username='TEST_USER', password='TEST_PASSWORD')

    def test_logout(self):
        self.client.post('/authentication/login/', {
            'username': 'TEST_USER',
            'password': 'TEST_PASSWORD',
        })

        response = self.client.get('/authentication/logout/')
        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url, '/')

        response = self.client.get('/')
        self.assertFalse(response.context['user'].is_authenticated)


class RegisterTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register_page(self):
        response = self.client.get('/authentication/register/')
        self.assertEqual(response.status_code, 200)

    def test_register_correct(self):
        response = self.client.post('/authentication/register/', {
            'username': 'TEST_USER',
            'password': 'TEST_PASSWORD',
            'firstName': 'TEST_FIRST_NAME',
            'lastName': 'TEST_LAST_NAME',
            'email': 'TEST@EMAIL.com',
            'passwordConfirm': 'TEST_PASSWORD',
        })
        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url, '/')

        response = self.client.get('/')
        self.assertTrue(response.context['user'].is_authenticated)

    def test_register_username_taken(self):
        User.objects.create_user(username='TEST_USER', password='TEST_PASSWORD')

        response = self.client.post('/authentication/register/', {
            'username': 'TEST_USER',
            'password': 'TEST_PASSWORD',
            'firstName': 'TEST_FIRST_NAME',
            'lastName': 'TEST_LAST_NAME',
            'email': 'test@gmail.com',
            'passwordConfirm': 'TEST_PASSWORD',
        })
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_register_email_taken(self):
        User.objects.create_user(username='ANOTHER_USER', password='TEST_PASSWORD', email='test@gmail.com')

        response = self.client.post('/authentication/register/', {
            'username': 'TEST_USER',
            'password': 'TEST_PASSWORD',
            'firstName': 'TEST_FIRST_NAME',
            'lastName': 'TEST_LAST_NAME',
            'email': 'test@gmail.com',
            'passwordConfirm': 'TEST_PASSWORD',
        })
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_register_password_dont_match(self):
        response = self.client.post('/authentication/register/', {
            'username': 'TEST_USER',
            'password': 'TEST_PASSWORD',
            'firstName': 'TEST_FIRST_NAME',
            'lastName': 'TEST_LAST_NAME',
            'email': 'test@gmail.com',
            'passwordConfirm': 'ANOTHER_PASSWORD',
        })
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_register_email_missing(self):
        response = self.client.post('/authentication/register/', {
            'username': 'TEST_USER',
            'password': 'TEST_PASSWORD',
            'firstName': 'TEST_FIRST_NAME',
            'lastName': 'TEST_LAST_NAME',
            'passwordConfirm': 'ANOTHER_PASSWORD',
        })
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_register_first_name_missing(self):
        response = self.client.post('/authentication/register/', {
            'username': 'TEST_USER',
            'password': 'TEST_PASSWORD',
            'lastName': 'TEST_LAST_NAME',
            'email': 'test@gmail.com',
            'passwordConfirm': 'ANOTHER_PASSWORD',
        })
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_register_last_name_missing(self):
        response = self.client.post('/authentication/register/', {
            'username': 'TEST_USER',
            'password': 'TEST_PASSWORD',
            'firstName': 'TEST_FIRST_NAME',
            'email': 'test@gmail.com',
            'passwordConfirm': 'ANOTHER_PASSWORD',
        })
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_register_username_name_missing(self):
        response = self.client.post('/authentication/register/', {
            'password': 'TEST_PASSWORD',
            'firstName': 'TEST_FIRST_NAME',
            'lastName': 'TEST_LAST_NAME',
            'email': 'test@gmail.com',
            'passwordConfirm': 'ANOTHER_PASSWORD',
        })
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)


class LoginTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create_user(username='TEST_USER', password='TEST_PASSWORD')

    def test_login_page(self):
        response = self.client.get('/authentication/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_correct(self):
        response = self.client.post('/authentication/login/', {
            'username':'TEST_USER',
            'password': 'TEST_PASSWORD',
        })
        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url, '/')

        response = self.client.get('/')
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_fail(self):
        response = self.client.post('/authentication/login/', {
            'username': 'TEST_USER',
            'password': 'WRONG_PASSWORD',
        })
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_login_without_username(self):
        response = self.client.post('/authentication/login/', {
            'password': 'WRONG_PASSWORD',
        })
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_login_without_password(self):
        response = self.client.post('/authentication/login/', {
            'username': 'TEST_USER',
        })
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
