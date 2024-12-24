from django.contrib import admin
from withdrawals.models import Withdraw

class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'created_on')
    list_filter = ('created_on', 'user')
    search_fields = ('user__username',)
    fields = ('user', 'amount', 'created_on')
    readonly_fields = ('created_on',)

admin.site.register(Withdraw, WithdrawAdmin)
