from django.db import models
from accounts.models import VirtualAccount
from uuid import uuid4

class TransactionStatus(models.TextChoices):
    PENDING = 'pending', 'En cours'
    SUCCESS = 'success', 'Réussi'
    FAILED = 'failed', 'Échoué'

class TypeTransaction(models.TextChoices):
    DEPOSIT = 'deposit', 'Dépôt'
    TRANSFER = 'transfer', 'Transfert'
    WITHDRAWAL = 'withdrawal', 'Retrait'
    FEE = 'fee', 'Commission'

class Transaction(models.Model):
    reference = models.CharField(max_length=36, unique=True, editable=False)
    type = models.CharField(max_length=20, choices=TypeTransaction.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=TransactionStatus.choices, default=TransactionStatus.SUCCESS)
    sender_account = models.ForeignKey(VirtualAccount, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver_account = models.ForeignKey(
        VirtualAccount,
        on_delete=models.CASCADE,
        related_name='received_transactions',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_status_display()}] {self.get_type_display()} de {self.amount} FCFA"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = str(uuid4())
        super().save(*args, **kwargs)