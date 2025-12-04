from django.contrib import admin
from authentication.admin import admin_site
from .models import StudentSpace


@admin.register(StudentSpace, site=admin_site)
class StudentSpaceAdmin(admin.ModelAdmin):
    """
    Admin interface for StudentSpace model
    """
    list_display = ('id', 'student', 'name', 'is_primary', 'is_public', 'created_at')
    list_filter = ('is_primary', 'is_public', 'created_at', 'student__class_assignment__school')
    search_fields = ('student__name', 'name', 'url', 'student__generated_email')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['student']

    fieldsets = (
        ('학생 정보', {
            'fields': ('student',)
        }),
        ('스페이스 정보', {
            'fields': ('name', 'url', 'space_id', 'description')
        }),
        ('설정', {
            'fields': ('is_primary', 'is_public')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
