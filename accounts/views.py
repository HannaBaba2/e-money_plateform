# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from .models import User, VirtualAccount
from core.utils import create_otp
from django.utils import timezone




def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.status = 'pending'
            user.save()
            create_otp(user, minutes=2)
            request.session['user_id'] = user.id
            messages.info(request, "Un code OTP vous a été envoyé par e-mail.")
            return redirect('verify_otp')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        user_id = request.session.get('user_id')
        if user_id:
            from core.models import OTP
            try:
                otp = OTP.objects.filter(user_id=user_id, code=otp_code).latest('created_at')
                if otp.is_valid():
                    user = otp.user
                    user.status = 'active'
                    user.save()
                    VirtualAccount.objects.get_or_create(user=user)
                    login(request, user)
                    messages.success(request, "Compte activé avec succès !")
                    return redirect('dashboard')
                else:
                    messages.error(request, "OTP expiré .")
            except OTP.DoesNotExist:
                messages.error(request, "OTP invalide.")
        else:
            messages.error(request,"Session invalide.")
    return render(request, 'accounts/verify_otp.html')

@login_required
def dashboard(request):
    if request.user.status == 'suspended':
        return render(request, 'accounts/dashboard.html', {'suspended': True})
    
    # Récupère les 10 dernières transactions de l'utilisateur
    transactions = request.user.virtualaccount.sent_transactions.order_by('-created_at')[:10]
    
    return render(request, 'accounts/dashboard.html', {
        'suspended': False,
        'transactions': transactions
    })


def logout_view(request):
    logout(request)
    return redirect('signup')



# accounts/views.py - dans dashboard


