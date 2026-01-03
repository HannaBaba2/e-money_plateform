# transactions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.deposit_view, name='deposit'),
    path('transfer/', views.transfer_view, name='transfer'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('confirm-withdraw/', views.confirm_withdraw_view, name='confirm_withdraw'),
]