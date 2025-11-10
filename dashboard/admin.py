from django.contrib import admin
from dashboard.models import VisitorLog


@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    """Admin interface for VisitorLog model"""
    list_display = ['timestamp', 'ip_address', 'path']
    list_filter = ['timestamp', 'path']
    search_fields = ['ip_address']
    readonly_fields = ['timestamp', 'ip_address', 'user_agent', 'path']

    def has_add_permission(self, request):
        # Prevent manual creation - logs are auto-generated
        return False
