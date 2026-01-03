# core/utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import OTP
import random

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp_code):
    send_mail(
        'Votre code OTP - eMoney',
        f'Votre code de vérification est : {otp_code}\nValable 2 minutes.',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

def create_otp(user, minutes=2):
    from datetime import timedelta
    otp_code = generate_otp()
    expire_at = timezone.now() + timedelta(minutes=minutes)
    otp = OTP.objects.create(
        code=otp_code,
        user=user,
        expire_at=expire_at
    )
    send_otp_email(user.email, otp_code)
    return otp