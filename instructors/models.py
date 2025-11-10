from django.db import models
from django.conf import settings


class Instructor(models.Model):
    """
    Instructor profile linked to User with role='instructor'.

    Stores instructor-specific information beyond the base User model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        limit_choices_to={'role': 'instructor'},
        verbose_name='사용자 계정'
    )
    affiliated_school = models.ForeignKey(
        'students.School',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instructors',
        verbose_name='소속 학교',
        help_text='강사 소속 학교'
    )
    training_completed = models.BooleanField(
        default=False,
        verbose_name='연수 완료 여부',
        help_text='강사 연수 이수 상태'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일'
    )

    class Meta:
        verbose_name = '강사'
        verbose_name_plural = '강사'
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    @property
    def class_count(self):
        """Count of classes assigned to this instructor."""
        return self.user.taught_classes.count()
