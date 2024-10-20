from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


user_model = get_user_model()


class UserRegisterTest(APITestCase):
    def setUp(self):
        self.url = reverse('auth-register')

    def test_success_register(self):
        data = {'username': 'test_user', 'password': 'secret123Test'}
        response = self.client.post(self.url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED, response.json())

    def test_failure_on_exists_user(self):
        user_model.objects.create_user(username="exists", password="secret")

        data = {'username': 'exists', 'password': 'secret123Test'}
        response = self.client.post(self.url, data, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEquals(response.status_code, status.HTTP_201_CREATED, response.json())

    def test_failure_username_unicode_validation(self):
        data = {'username': '', 'password': 'secret123Ad'}
        response = self.client.post(self.url, data, format='json')
        resp_data = response.json()
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", resp_data)

        data = {'username': '\xe4\xb8\xad\xe6\x96\x87', 'password': 'secret123Ad'}
        response = self.client.post(self.url, data, format='json')
        resp_data = response.json()
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", resp_data)

    def test_password_validation(self):
        common_pwd = 'secret123'
        response = self.client.post(self.url, {"username": "test", "password": common_pwd}, format='json')
        resp_data = response.json()
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", resp_data)
