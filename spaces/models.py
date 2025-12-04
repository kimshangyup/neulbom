from django.db import models


class StudentSpace(models.Model):
    """
    ZEP Space model allowing multiple spaces per student

    A student can have multiple ZEP spaces for different purposes
    (e.g., portfolio, project, exhibition, etc.)
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='spaces',
        verbose_name='학생'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='공간 이름',
        help_text='ZEP 공간의 이름 (예: 포트폴리오, 프로젝트 A 등)'
    )
    url = models.URLField(
        max_length=500,
        verbose_name='ZEP 스페이스 URL',
        help_text='ZEP 스페이스 URL'
    )
    space_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ZEP 스페이스 ID',
        help_text='ZEP API에서 반환된 스페이스 ID'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='대표 공간',
        help_text='학생의 대표 공간 여부'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='공개 여부',
        help_text='랜딩 페이지에 공개할지 여부'
    )
    description = models.TextField(
        blank=True,
        verbose_name='설명',
        help_text='공간에 대한 설명'
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
        verbose_name = 'ZEP 스페이스'
        verbose_name_plural = 'ZEP 스페이스'
        ordering = ['-is_primary', '-created_at']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['is_primary']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.name}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset other primary spaces for this student
        if self.is_primary:
            StudentSpace.objects.filter(
                student=self.student,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
