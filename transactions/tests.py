from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import VirtualAccount
from .utils import deposit, transfer,withdraw
from .models import Transaction, TypeTransaction, TransactionStatus
from core.models import OTP
from core.utils import create_otp


User = get_user_model()

class DepositTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test1234",
            status="active"
        )
        VirtualAccount.objects.create(user=self.user)

    def test_deposit_positive_amount(self):
        deposit(self.user, 5000)
        self.assertEqual(self.user.virtualaccount.balance, 5000)
        
        tx = self.user.virtualaccount.sent_transactions.first()
        self.assertEqual(tx.type, TypeTransaction.DEPOSIT)
        self.assertEqual(tx.amount, 5000)
        self.assertEqual(tx.net_amount, 5000)
        self.assertEqual(tx.status, TransactionStatus.SUCCESS)
        self.assertIsNotNone(tx.reference)
        self.assertEqual(len(tx.reference), 36)

    def test_deposit_view_status_200(self):
        self.client.login(username="testuser", password="test1234")
        response = self.client.get("/transactions/deposit/")
        self.assertEqual(response.status_code, 200)

    def test_deposit_invalid_amount(self):
        with self.assertRaises(ValueError):
            deposit(self.user, -100)
        with self.assertRaises(ValueError):
            deposit(self.user, 0)


class TransferTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@test.com",
            password="pass1234",
            phone_number="98765432",
            status="active"
        )
        self.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@test.com",
            password="pass1234",
            phone_number="12345678",
            status="active"
        )
        VirtualAccount.objects.create(user=self.sender, balance=10000)
        VirtualAccount.objects.create(user=self.receiver)

    def test_transfer_success(self):
        transfer(self.sender, "12345678", 2000)
        self.sender.refresh_from_db()
        self.receiver.refresh_from_db()
        self.assertEqual(self.sender.virtualaccount.balance, 8000)
        self.assertEqual(self.receiver.virtualaccount.balance, 2000)
        
        tx = Transaction.objects.get(type=TypeTransaction.TRANSFER)
        self.assertEqual(tx.amount, 2000)
        self.assertEqual(tx.sender_account.user, self.sender)
        self.assertEqual(tx.receiver_account.user, self.receiver)

    def test_transfer_to_inactive_user(self):
        self.receiver.status = 'suspended'
        self.receiver.save()
        with self.assertRaises(ValueError):
            transfer(self.sender, "12345678", 1000)

    def test_transfer_insufficient_funds(self):
        with self.assertRaises(ValueError):
            transfer(self.sender, "12345678", 15000)





class WithdrawalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test1234",
            status="active"
        )
        VirtualAccount.objects.create(user=self.user, balance=10000)
        platform_user = User.objects.create_user(
            username="platform",
            email="p@p.com",
            password="p",
            status="active"
        )
        VirtualAccount.objects.create(user=platform_user)

    def test_withdrawal_success(self):
        create_otp(self.user, minutes=3)
        otp = OTP.objects.filter(user=self.user).latest('created_at')
        
        withdraw(self.user, 1000)
        
        self.user.virtualaccount.refresh_from_db()
        self.assertEqual(self.user.virtualaccount.balance, 9000)
        
        withdrawal_tx = Transaction.objects.get(type=TypeTransaction.WITHDRAWAL)
        fee_tx = Transaction.objects.get(type=TypeTransaction.FEE)
        
        self.assertEqual(withdrawal_tx.net_amount, 980)
        self.assertEqual(fee_tx.amount, 20)
        self.assertEqual(fee_tx.receiver_account.user.username, "platform")

    def test_withdrawal_insufficient_funds(self):
        with self.assertRaises(ValueError):
            withdraw(self.user, 15000)