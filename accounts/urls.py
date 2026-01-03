# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]