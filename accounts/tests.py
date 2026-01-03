# accounts/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from .models import User

class AccountCreationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_page_loads(self):
        """Test que la page d'inscription charge (status 200)"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_signup(self):
        """Test de l'inscription complète"""
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_number': '98765432',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123'
        })
        # Doit rediriger vers verify-otp
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertEqual(user.status, 'pending')