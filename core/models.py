# core/models.py
from django.db import models
from accounts.models import User, TimeStampMixin  # ← importe TimeStampMixin

class OTP(TimeStampMixin):  # ← Hérite du mixin
    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    expire_at = models.DateTimeField()
    is_expired = models.BooleanField(default=False)

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if now > self.expire_at:
            self.is_expired = True
            self.save()
            return False
        return not self.is_expired

    def __str__(self):
        return f"OTP {self.code} pour {self.user.username}"