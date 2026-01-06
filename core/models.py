from django.db import models
from django.utils import timezone
from accounts.models import User, TimeStampMixin

class OTP(TimeStampMixin):
    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    expire_at = models.DateTimeField()
    is_expired = models.BooleanField(default=False)

    def is_valid(self):
        now = timezone.now()  
        if now > self.expire_at:
            if not self.is_expired:
                self.is_expired = True
                self.save(update_fields=['is_expired'])
            return False
        return True 
        

    def __str__(self):
        return f"OTP {self.code} pour {self.user.username}"