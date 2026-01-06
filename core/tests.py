from django.test import TestCase
from django.utils import timezone
from .models import OTP
from accounts.models import User

class OTPTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test1234"
        )

    def test_otp_valid(self):
        otp = OTP.objects.create(
            code="123456",
            user=self.user,
            expire_at=timezone.now() + timezone.timedelta(minutes=2)
        )
        self.assertTrue(otp.is_valid())

    def test_otp_expired(self):
        otp = OTP.objects.create(
            code="123456",
            user=self.user,
            expire_at=timezone.now() - timezone.timedelta(minutes=1)
        )
        self.assertFalse(otp.is_valid())
        self.assertTrue(otp.is_expired)

    def test_otp_has_timestamps(self):
        otp = OTP.objects.create(
            code="123456",
            user=self.user,
            expire_at=timezone.now() + timezone.timedelta(minutes=2)
        )
        self.assertIsNotNone(otp.created_at)
        self.assertIsNotNone(otp.updated_at)