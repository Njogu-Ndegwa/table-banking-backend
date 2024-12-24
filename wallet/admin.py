from django.contrib import admin
from wallet.models import Wallet, UserWallet
from .models import Contribution

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('user_wallet', 'amount', 'date')
    list_filter = ('date',)
    search_fields = ('user_wallet__user__username',)
    ordering = ('-date',)

class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'name', 'balance', 'total_balance')
    list_filter = ('owner',)
    search_fields = ('name', 'owner__username')
    fields = ('owner', 'name', 'balance', 'total_balance')
    readonly_fields = ('balance', 'total_balance')

class UserWalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet', 'balance')
    list_filter = ('user', 'wallet')
    search_fields = ('user__username', 'wallet__name')
    fields = ('user', 'wallet', 'balance')
    readonly_fields = ('balance',)

admin.site.register(Wallet, WalletAdmin)
admin.site.register(UserWallet, UserWalletAdmin)
