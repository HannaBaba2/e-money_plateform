from decimal import Decimal
from django.db import transaction as db_transaction
from accounts.models import VirtualAccount, User
from .models import Transaction, TypeTransaction, TransactionStatus
import logging

logger = logging.getLogger(__name__)

PLATFORM_FEE_RATE = Decimal('0.02')  

def deposit(user, amount):
    if amount <= 0:
        raise ValueError("Le montant du dépôt doit être positif.")
    
    with db_transaction.atomic():
        account = user.virtualaccount
        account.balance += amount
        account.save()
        
        transaction = Transaction(
            type=TypeTransaction.DEPOSIT,
            amount=amount,
            fee=Decimal('0'),
            net_amount=amount,
            status=TransactionStatus.SUCCESS,
            sender_account=account,
            receiver_account=account
        )
        transaction.save()
        
        logger.info(
            f"[DÉPÔT] {user.username} a déposé {amount} FCFA. "
            f"Référence: {transaction.reference}. Nouveau solde: {account.balance} FCFA"
        )

def transfer(sender_user, receiver_phone, amount):
    if amount <= 0:
        raise ValueError("Le montant du transfert doit être positif.")
    
    with db_transaction.atomic():
        sender_account = sender_user.virtualaccount
        try:
            receiver_user = User.objects.get(phone_number=receiver_phone, status='active')
            receiver_account = receiver_user.virtualaccount
        except User.DoesNotExist:
            raise ValueError("Destinataire introuvable ou compte inactif.")

        if sender_account.balance < amount:
            raise ValueError("Solde insuffisant pour effectuer le transfert.")

        sender_account.balance -= amount
        receiver_account.balance += amount
        sender_account.save()
        receiver_account.save()

        transaction = Transaction(
            type=TypeTransaction.TRANSFER,
            amount=amount,
            fee=Decimal('0'),
            net_amount=amount,
            status=TransactionStatus.SUCCESS,
            sender_account=sender_account,
            receiver_account=receiver_account
        )
        transaction.save()

        logger.info(
            f"[TRANSFERT] '{sender_user.username}'  '{receiver_user.username}' : {amount} FCFA. "
            f"Référence: {transaction.reference}. Solde émetteur: {sender_account.balance} FCFA"
        )

def withdraw(user, amount):
    if amount <= 0:
        raise ValueError("Le montant du retrait doit être positif.")
    
    with db_transaction.atomic():
        account = user.virtualaccount
        if account.balance < amount:
            raise ValueError("Solde insuffisant pour effectuer le retrait.")

        fee_amount = amount * PLATFORM_FEE_RATE
        net_amount = amount - fee_amount

        account.balance -= amount
        account.save()

        withdrawal_tx = Transaction(
            type=TypeTransaction.WITHDRAWAL,
            amount=net_amount,
            fee=Decimal('0'),
            net_amount=net_amount,
            status=TransactionStatus.SUCCESS,
            sender_account=account,
            receiver_account=None
        )
        withdrawal_tx.save()

        try:
            platform_user = User.objects.get(username='platform')
            platform_account = platform_user.virtualaccount
        except User.DoesNotExist:
            raise RuntimeError("Compte plateforme 'platform' non trouvé. Créez-le via le shell.")

        fee_tx = Transaction(
            type=TypeTransaction.FEE,
            amount=fee_amount,
            fee=fee_amount,
            net_amount=Decimal('0'),
            status=TransactionStatus.SUCCESS,
            sender_account=account,
            receiver_account=platform_account
        )
        fee_tx.save()

        platform_account.balance += fee_amount
        platform_account.save()

        logger.info(
            f"[RETRAIT] {user.username} a retiré {net_amount} FCFA (frais: {fee_amount} FCFA). "
            f"Réf. retrait: {withdrawal_tx.reference}, Réf. frais: {fee_tx.reference}. "
            f"Solde: {account.balance} FCFA"
        )