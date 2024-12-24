# admin.py
from django.contrib import admin
from .models import LoanProposal, LoanProposalVote

@admin.register(LoanProposal)
class LoanProposalAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet', 'amount', 'reason', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'reason')
    ordering = ('-created_at',)

@admin.register(LoanProposalVote)
class LoanProposalVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'proposal', 'vote', 'created_at')
    list_filter = ('vote', 'created_at')
    search_fields = ('user__username', 'proposal__reason')
    ordering = ('-created_at',)
