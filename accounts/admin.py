from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from .models import User, VirtualAccount
import logging

logger = logging.getLogger(__name__)

@admin.action(description="Suspendre les utilisateurs sélectionnés")
def suspend_users(modeladmin, request, queryset):
    for user in queryset:
        if user.status != 'suspended':
            user.status = 'suspended'
            user.save()
            logger.info(f"[ADMIN] Utilisateur '{user.username}' suspendu par {request.user.username}")
    messages.success(request, "Les utilisateurs sélectionnés ont été suspendus.")

@admin.action(description="Réactiver les utilisateurs sélectionnés")
def reactivate_users(modeladmin, request, queryset):
    for user in queryset:
        if user.status != 'active':
            user.status = 'active'
            user.save()
            logger.info(f"[ADMIN] Utilisateur '{user.username}' réactivé par {request.user.username}")
    messages.success(request, "Les utilisateurs sélectionnés ont été réactivés.")

class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone_number', 'status', 'is_staff']
    list_filter = ['status', 'is_staff', 'is_superuser']
    actions = [suspend_users, reactivate_users]
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations eMoney', {
            'fields': ('phone_number', 'status'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number',),
        }),
    )

admin.site.register(User, UserAdmin)


@admin.register(VirtualAccount)
class VirtualAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return True  
    
    def has_delete_permission(self, request, obj=None):
        return True  