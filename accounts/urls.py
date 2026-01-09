from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/metrics/', views.admin_metrics, name='admin_metrics'),
    path('admin/metrics/user/<int:user_id>/', views.admin_metrics, name='admin_metrics_with_id'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),       
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'),
]