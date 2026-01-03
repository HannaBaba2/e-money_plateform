# transactions/views.py
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import deposit, transfer,withdraw
from core.utils import create_otp

# --- Dépôt & Transfert (inchangés) ---
@login_required
def deposit_view(request):
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get("amount"))
            if amount <= 0:
                messages.error(request, "Le montant doit être positif.")
            else:
                deposit(request.user, amount)
                messages.success(request, f"Dépôt de {amount} FCFA effectué.")
                return redirect("dashboard")
        except (ValueError, TypeError):
            messages.error(request, "Montant invalide.")
    return render(request, "transactions/deposit.html")

@login_required
def transfer_view(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        try:
            amount = Decimal(request.POST.get("amount"))
        except (ValueError, TypeError):
            messages.error(request, "Montant invalide.")
            return render(request, "transactions/transfer.html")
        
        if not phone or amount <= 0:
            messages.error(request, "Veuillez remplir tous les champs avec des valeurs valides.")
            return render(request, "transactions/transfer.html")
        
        try:
            transfer(request.user, phone, amount)
            messages.success(request, f"Transfert de {amount} FCFA vers {phone} effectué.")
            return redirect("dashboard")
        except ValueError as e:
            messages.error(request, str(e))
    
    return render(request, "transactions/transfer.html")

# --- RETRAIT (nouveau) ---
@login_required
def withdraw_view(request):
    """Étape 1 : Demande le montant et envoie l'OTP (3 min)."""
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get("amount"))
        except (ValueError, TypeError):
            messages.error(request, "Montant invalide.")
            return render(request, "transactions/withdraw.html")
        
        if amount <= 0:
            messages.error(request, "Le montant doit être positif.")
            return render(request, "transactions/withdraw.html")
        
        # Vérifie le solde
        if request.user.virtualaccount.balance < amount:
            messages.error(request, "Solde insuffisant.")
            return render(request, "transactions/withdraw.html")
        
        # Envoie OTP de retrait (3 minutes)
        create_otp(request.user, minutes=3)
        request.session['withdraw_amount'] = str(amount)
        messages.info(request, "Un code de sécurité vous a été envoyé par e-mail (valable 3 min).")
        return redirect("confirm_withdraw")
    
    return render(request, "transactions/withdraw.html")

@login_required
def confirm_withdraw_view(request):
    """Étape 2 : Confirme le retrait avec OTP."""
    amount_str = request.session.get('withdraw_amount')
    if not amount_str:
        messages.error(request, "Aucun retrait en cours.")
        return redirect("withdraw")
    
    try:
        amount = Decimal(amount_str)
    except:
        messages.error(request, "Montant invalide.")
        return redirect("withdraw")
    
    if request.method == "POST":
        otp_code = request.POST.get("otp")
        try:
            # Récupère le dernier OTP de l'utilisateur
            from core.models import OTP
            otp = OTP.objects.filter(
                user=request.user,
                code=otp_code
            ).latest('created_at')
            
            if not otp.is_valid():
                messages.error(request, "Code expiré ou invalide.")
                return render(request, "transactions/confirm_withdraw.html")
            
            # Effectue le retrait
            withdraw(request.user, amount)
            del request.session['withdraw_amount']
            messages.success(request, f"Retrait de {amount} FCFA effectué.")
            return redirect("dashboard")
        
        except OTP.DoesNotExist:
            messages.error(request, "Code de sécurité invalide.")
    
    return render(request, "transactions/confirm_withdraw.html")