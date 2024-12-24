# admin.py
from django.contrib import admin
from .models import InterestEarned

@admin.register(InterestEarned)
class InterestEarnedAdmin(admin.ModelAdmin):
    list_display = ('user', 'loan_repayment', 'interest_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'loan_repayment__id')
    ordering = ('-created_at',)
