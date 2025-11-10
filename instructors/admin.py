from django.contrib import admin
from .models import Instructor


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    """Admin interface for Instructor model."""
    list_display = ['user', 'affiliated_school', 'training_completed', 'created_at']
    list_filter = ['training_completed', 'affiliated_school', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('사용자 정보', {
            'fields': ('user',)
        }),
        ('강사 정보', {
            'fields': ('affiliated_school', 'training_completed')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
