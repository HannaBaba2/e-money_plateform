from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator


class TimeStampMixin(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

class UserStatus(models.TextChoices):
    PENDING = 'pending', 'En attente'     
    ACTIVE = 'active', 'Actif'            
    SUSPENDED = 'suspended', 'Suspendu'

class Gender(models.TextChoices):
    MALE = 'M', 'Masculin'
    FEMALE = 'F', 'Féminin'
    OTHER = 'X', 'Non précisé'

class User(AbstractUser, TimeStampMixin):
    phone_number = models.CharField(max_length=8, unique=True, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.OTHER)
    status = models.CharField(max_length=10, choices=UserStatus.choices, default=UserStatus.PENDING)
    is_suspended = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.is_suspended = (self.status == UserStatus.SUSPENDED)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_status_display()})"

class VirtualAccount(TimeStampMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='virtualaccount')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0,validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.balance} FCFA"