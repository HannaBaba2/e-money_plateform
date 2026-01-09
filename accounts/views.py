from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from .models import User, VirtualAccount
from core.utils import create_otp
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum



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
    
    transactions = request.user.virtualaccount.sent_transactions.order_by('-created_at')[:10]
    
    return render(request, 'accounts/dashboard.html', {
        'suspended': False,
        'transactions': transactions
    })


def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')  





def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.status == 'active':
                login(request, user)
                if user.is_staff:
                    return redirect('admin_metrics')
                else:
                    return redirect('dashboard')
            else:
                messages.error(request, "Votre compte est suspendu ou en attente d'activation.")
        else:
            messages.error(request, "Identifiants invalides.")
    return render(request, 'accounts/login.html')




@staff_member_required
def admin_metrics(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
        if request.method == "POST":
            action = request.POST.get("action")
            if action == "suspend":
                user.status = "suspended"
                user.is_suspended = True
                messages.success(request, f"Utilisateur {user.username} suspendu.")
            elif action == "reactivate":
                user.status = "active"
                user.is_suspended = False
                messages.success(request, f"Utilisateur {user.username} réactivé.")
            user.save()
            return redirect('admin_metrics_with_id', user_id=user.id)

        return render(request, 'admin/user_detail.html', {
            'user': user,
            'show_suspend': user.status == 'active',
            'show_reactivate': user.status == 'suspended',
        })

    users = User.objects.all().order_by('-created_at')
    total_users = users.count()
    active_users = users.filter(status='active').count()
    suspended_users = users.filter(status='suspended').count()
    pending_users = users.filter(status='pending').count()

    return render(request, 'admin/user_list.html', {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'suspended_users': suspended_users,
        'pending_users': pending_users or 0,
    })