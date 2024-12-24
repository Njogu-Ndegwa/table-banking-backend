# admin.py
from django.contrib import admin
from .models import Shares

@admin.register(Shares)
class SharesAdmin(admin.ModelAdmin):
    list_display = ('user', 'share_change', 'share_percentage', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username',)
    ordering = ('-timestamp',)
