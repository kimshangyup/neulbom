from django.contrib import admin
from authentication.admin import admin_site
from .models import School, Class, Student, FailedSpaceCreation


@admin.register(School, site=admin_site)
class SchoolAdmin(admin.ModelAdmin):
    """
    Admin interface for School model
    """
    list_display = ('name', 'contact_phone', 'contact_email', 'created_at')
    search_fields = ('name', 'address', 'contact_email')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'logo', 'address')
        }),
        ('연락처', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Class, site=admin_site)
class ClassAdmin(admin.ModelAdmin):
    """
    Admin interface for Class model
    """
    list_display = ('name', 'school', 'instructor', 'academic_year', 'semester', 'student_count')
    list_filter = ('academic_year', 'semester', 'school')
    search_fields = ('name', 'school__name', 'instructor__username', 'instructor__first_name', 'instructor__last_name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['school', 'instructor']

    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'school', 'instructor')
        }),
        ('학기 정보', {
            'fields': ('academic_year', 'semester')
        }),
        ('추가 정보', {
            'fields': ('description',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def student_count(self, obj):
        """Display number of students in class"""
        return obj.students.count()
    student_count.short_description = '학생 수'


@admin.register(Student, site=admin_site)
class StudentAdmin(admin.ModelAdmin):
    """
    Admin interface for Student model
    """
    list_display = ('id', 'name', 'class_number', 'grade', 'class_assignment', 'academic_year_display', 'has_zep_space', 'created_at')
    list_filter = ('grade', 'class_number', 'class_assignment__academic_year', 'class_assignment__semester', 'class_assignment__school', 'class_assignment')
    search_fields = ('id', 'name', 'generated_email', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at', 'generated_email')
    autocomplete_fields = ['user', 'class_assignment']

    fieldsets = (
        ('기본 정보', {
            'fields': ('id', 'user', 'name', 'class_number', 'grade')
        }),
        ('학급 정보', {
            'fields': ('class_assignment',)
        }),
        ('계정 정보', {
            'fields': ('generated_email',)
        }),
        ('ZEP 스페이스', {
            'fields': ('zep_space_url',)
        }),
        ('추가 정보', {
            'fields': ('notes',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_zep_space(self, obj):
        """Display whether student has ZEP space"""
        return bool(obj.zep_space_url)
    has_zep_space.short_description = 'ZEP 스페이스'
    has_zep_space.boolean = True

    def academic_year_display(self, obj):
        """Display academic year and semester from class assignment"""
        if obj.class_assignment:
            return f"{obj.class_assignment.academic_year} {obj.class_assignment.get_semester_display()}"
        return '-'
    academic_year_display.short_description = '학년도'


@admin.register(FailedSpaceCreation, site=admin_site)
class FailedSpaceCreationAdmin(admin.ModelAdmin):
    """
    Admin interface for FailedSpaceCreation model
    """
    list_display = ('student', 'retry_count', 'resolved', 'last_attempted_at', 'created_at')
    list_filter = ('resolved', 'created_at')
    search_fields = ('student__name', 'student__generated_email', 'error_message')
    readonly_fields = ('created_at', 'last_attempted_at')

    fieldsets = (
        ('학생 정보', {
            'fields': ('student',)
        }),
        ('오류 정보', {
            'fields': ('error_message', 'retry_count', 'last_attempted_at')
        }),
        ('해결 상태', {
            'fields': ('resolved', 'resolved_at')
        }),
        ('시스템 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
