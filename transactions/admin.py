from django.contrib import admin
from .models import Transaction, TypeTransaction, TransactionStatus

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'reference',
        'type_display',
        'amount',
        'fee',
        'net_amount',
        'status_display',
        'sender_user',
        'receiver_user',
        'created_at'
    ]
    
    list_filter = ['type', 'status', 'created_at']
    
    search_fields = [
        'reference',
        'sender_account__user__username',
        'receiver_account__user__username'
    ]
    
    readonly_fields = [
        'reference',
        'type',
        'amount',
        'fee',
        'net_amount',
        'status',
        'sender_account',
        'receiver_account',
        'created_at'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    def type_display(self, obj):
        return obj.get_type_display()
    type_display.short_description = 'Type'
    type_display.admin_order_field = 'type'

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Statut'
    status_display.admin_order_field = 'status'

    def sender_user(self, obj):
        return obj.sender_account.user.username
    sender_user.short_description = 'Émetteur'
    sender_user.admin_order_field = 'sender_account__user__username'

    def receiver_user(self, obj):
        if obj.receiver_account:
            return obj.receiver_account.user.username
        if obj.type == TypeTransaction.WITHDRAWAL:
            return "—"
        if obj.type == TypeTransaction.FEE:
            return "Plateforme"
        return "—"
    receiver_user.short_description = 'Destinataire'