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
            'username': 'TEST_USER',
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

class AccountTestCase(TestCase):
    TEST_USERNAME = 'TEST_USERNAME'
    TEST_PASS = 'TEST_PASSWORD'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username=self.TEST_USERNAME,
            password=self.TEST_PASS,
        )

    def test_user_redirect_when_not_logged_in(self):
        response = self.client.get('/authentication/account', follow=True)
        final_url = response.redirect_chain[-1]
        self.assertEqual(final_url[0], '/')

    def test_user_does_not_redirect_when_logged_in(self):
        self.client.force_login(user=self.user)
        response = self.client.get('/authentication/account')
        self.assertEqual(response['location'], '/authentication/account/')

# TODO: Figure out how to test stuff that needs passwords
class ChangePasswordTestCase(TestCase):
    TEST_USERNAME = 'TEST_USERNAME'
    TEST_PASS = 'TEST_PASSWORD'
    NEW_PASS = 'TEST_PSWD'

    def setUp(self):
        self.client = Client()
        self.credentials = {
            'username': self.TEST_USERNAME,
            #'password': self.TEST_PASS,
        }
        self.user = User.objects.create(**self.credentials)
        #self.user.set_password(self.TEST_PASS)

    def test_user_redirect_when_not_logged_in(self):
        response = self.client.get('/authentication/change_pswd/', follow=True)
        final_url = response.redirect_chain[-1]
        self.assertEqual(final_url[0], '/')


class ChangeUsernameTestCase(TestCase):
    TEST_USERNAME = 'TEST_USERNAME'
    TEST_PASS = 'TEST_PASSWORD'
    NEW_PASS = 'TEST_PSWD'

    def setUp(self):
        self.client = Client()
        self.credentials = {
            'username': self.TEST_USERNAME,
        }
        self.user = User.objects.create(**self.credentials)
        #self.user.set_password(self.TEST_PASS)

    def test_change_username(self):
        return True
# End TODO
