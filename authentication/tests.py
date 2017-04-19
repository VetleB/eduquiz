from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from quiz.models import Player


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
        self.user = User.objects.create_user(
            username=self.TEST_USERNAME,
            password=self.TEST_PASS,
        )
        Player.objects.create(user=self.user)

    def test_user_redirect_when_not_logged_in(self):
        response = self.client.get('/authentication/account', follow=True)
        final_url = response.redirect_chain[-1]
        self.assertEqual(final_url[0], '/')

    def test_account_page(self):
        self.client.login(username=self.TEST_USERNAME, password=self.TEST_PASS)
        response = self.client.get('/authentication/account/')
        self.assertEqual(response.status_code, 200)


class ChangePasswordTestCase(TestCase):
    TEST_USERNAME = 'TEST_USERNAME'
    TEST_PASS = 'TEST_PASSWORD'
    NEW_PASS = 'TEST_PSWD'

    def setUp(self):
        self.client = Client()
        self.credentials = {
            'username': self.TEST_USERNAME,
            'password': self.TEST_PASS,
        }
        self.user = User.objects.create_user(**self.credentials)
        Player.objects.create(user=self.user)

    def test_change_password_page(self):
        self.client.login(**self.credentials)
        response = self.client.get('/authentication/change_pswd/')
        self.assertEqual(response.status_code, 200)

    def test_user_redirect_when_not_logged_in(self):
        response = self.client.get('/authentication/change_pswd/', follow=True)
        final_url = response.redirect_chain[-1]
        self.assertEqual(final_url[0], '/')

    def test_change_password_correct(self):
        self.client.login(**self.credentials)
        response = self.client.post('/authentication/change_pswd/', {
            'old_password': self.credentials['password'],
            'new_password1': 'NEW_PASSWORD',
            'new_password2': 'NEW_PASSWORD',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/authentication/account/')
        self.client.logout()

        old_login = self.client.login(username=self.credentials['username'], password=self.credentials['password'])
        self.client.logout()

        new_login = self.client.login(username=self.credentials['username'], password='NEW_PASSWORD')
        self.client.logout()

        self.assertFalse(old_login)
        self.assertTrue(new_login)


class ChangeUsernameTestCase(TestCase):
    TEST_USERNAME = 'TEST_USERNAME'
    TEST_PASS = 'TEST_PASSWORD'

    def setUp(self):
        self.client = Client()
        self.credentials = {
            'username': self.TEST_USERNAME,
            'password': self.TEST_PASS,
        }
        self.user = User.objects.create_user(**self.credentials)
        Player.objects.create(user=self.user)
        self.other_user = User.objects.create_user('OTHER_USERNAME', self.TEST_PASS)
        Player.objects.create(user=self.other_user)

    def test_change_name_page(self):
        self.client.login(**self.credentials)
        response = self.client.get('/authentication/change_name/')
        self.assertEqual(response.status_code, 200)

    def test_change_username_without_login(self):
        response = self.client.post('/authentication/change_name/', {
            'username': 'NEW_USERNAME',
            'password': self.credentials['password'],
        })
        self.assertNotEqual(response.status_code, 200)

    def test_change_username_correct(self):
        self.client.login(**self.credentials)
        response = self.client.post('/authentication/change_name/', {
            'username': 'NEW_USERNAME',
            'password': self.credentials['password'],
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/authentication/account/')

        response = self.client.get('/')
        self.assertEqual(response.context[0].dicts[1]['user'].username, 'NEW_USERNAME')

    def test_change_username_wrong_password(self):
        self.client.login(**self.credentials)
        response = self.client.post('/authentication/change_name/', {
            'username': 'NEW_USERNAME',
            'password': 'WRONG_PASSWORD',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context[0].dicts[1]['user'].username, 'NEW_USERNAME')

    def test_change_username_username_taken(self):
        self.client.login(**self.credentials)
        response = self.client.post('/authentication/change_name/', {
            'username': self.other_user.username,
            'password': self.credentials['password'],
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context[0].dicts[1]['user'].username, 'NEW_USERNAME')

    def test_change_username_no_fields(self):
        self.client.login(**self.credentials)
        response = self.client.post('/authentication/change_name/')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context[0].dicts[1]['user'].username, 'NEW_USERNAME')
