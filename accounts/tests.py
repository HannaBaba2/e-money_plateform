from django.test import TestCase, Client
from django.urls import reverse
from .models import User

class AccountCreationTests(TestCase):
    

    def test_signup_page_loads(self):
        
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_signup(self):
        
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'first_name': 'Test',         
            'last_name': 'User',           
            'email': 'test@example.com',
            'phone_number': '98765432',
            'gender': 'M',                 
            'password': 'SecurePass123!',   
            'confirm_password': 'SecurePass123!'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertEqual(user.status, 'pending')