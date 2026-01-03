# core/admin.py
from django.contrib import admin
from .models import OTP

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'user',
        'expire_at',
        'is_expired',
        'created_at',      # ← hérité de TimeStampMixin
        'updated_at'       # ← hérité de TimeStampMixin
    ]
    list_filter = ['is_expired', 'created_at', 'expire_at']
    search_fields = ['code', 'user__username', 'user__email']
    readonly_fields = [
        'code',
        'user',
        'expire_at',
        'is_expired',
        'created_at',
        'updated_at'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False