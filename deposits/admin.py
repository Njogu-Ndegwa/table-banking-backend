from django.contrib import admin
from deposits.models import Deposit
from datetime import datetime

class DepositAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'created_on')
    list_filter = ('created_on', 'user')
    search_fields = ('user__username',)
    fields = ('user', 'amount', 'created_on')
    readonly_fields = ('created_on',)

admin.site.register(Deposit, DepositAdmin)
