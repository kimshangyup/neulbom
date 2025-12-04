from django.db import models
from django.conf import settings


class School(models.Model):
    """
    School model for organizational hierarchy

    Represents schools participating in the Neulbom program.
    Each school is owned by the instructor who created it.
    """
    name = models.CharField(
        max_length=10,
        verbose_name='학교명',
        help_text='학교 이름 (최대 10글자)'
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='created_schools',
        limit_choices_to={'role': 'instructor'},
        verbose_name='생성 강사',
        help_text='이 학교를 생성한 강사'
    )
    logo = models.ImageField(
        upload_to='schools/logos/',
        null=True,
        blank=True,
        verbose_name='학교 로고',
        help_text='학교 로고 이미지'
    )
    address = models.TextField(
        blank=True,
        verbose_name='주소',
        help_text='학교 주소'
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='연락처',
        help_text='학교 대표 연락처'
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name='이메일',
        help_text='학교 대표 이메일'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='비고',
        help_text='학교 관련 메모'
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
        verbose_name = '학교'
        verbose_name_plural = '학교'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def class_count(self):
        """Returns number of classes in this school."""
        return self.classes.count()


class Class(models.Model):
    """
    Class model representing a teaching class

    Links instructor to their students within a specific academic period
    """
    SEMESTER_CHOICES = [
        ('spring', '1학기'),
        ('fall', '2학기'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='학급명',
        help_text='학급 이름 (예: 1학년 A반)'
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name='학교',
        help_text='소속 학교'
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taught_classes',
        limit_choices_to={'role': 'instructor'},
        verbose_name='담당 강사',
        help_text='학급 담당 강사'
    )
    academic_year = models.IntegerField(
        verbose_name='학년도',
        help_text='학년도 (예: 2025)'
    )
    semester = models.CharField(
        max_length=10,
        choices=SEMESTER_CHOICES,
        verbose_name='학기',
        help_text='학기 구분'
    )
    description = models.TextField(
        blank=True,
        verbose_name='설명',
        help_text='학급 설명 또는 특이사항'
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
        verbose_name = '학급'
        verbose_name_plural = '학급'
        ordering = ['-academic_year', 'semester', 'school', 'name']
        indexes = [
            models.Index(fields=['school', 'academic_year', 'semester']),
            models.Index(fields=['instructor']),
        ]

    def __str__(self):
        return f"{self.school.name} - {self.name} ({self.academic_year} {self.get_semester_display()})"

    def student_count(self):
        """Returns number of students in this class."""
        return self.students.count()


class Student(models.Model):
    """
    Student model representing elementary school students

    Links to User model for authentication and tracks ZEP space information
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'student'},
        verbose_name='사용자 계정'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='이름',
        help_text='학생 이름'
    )
    class_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='반 번호',
        help_text='학급 내 반 번호 (1반, 2반 등)'
    )
    grade = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='학년',
        help_text='학년 (1-6)'
    )
    class_assignment = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='소속 학급',
        help_text='현재 소속 학급'
    )
    generated_email = models.EmailField(
        unique=True,
        verbose_name='생성된 이메일',
        help_text='자동 생성된 이메일 주소'
    )
    zep_space_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='ZEP 스페이스 URL',
        help_text='학생 개인 ZEP 스페이스 URL'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='공개 여부',
        help_text='스페이스를 공개 랜딩 페이지에 표시할지 여부'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='비고',
        help_text='학생 관련 메모'
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
        verbose_name = '학생'
        verbose_name_plural = '학생'
        ordering = ['class_assignment', 'class_number', 'name']
        indexes = [
            models.Index(fields=['generated_email']),
            models.Index(fields=['class_assignment']),
        ]

    def __str__(self):
        class_info = f"{self.class_number}반 " if self.class_number else ""
        return f"{self.name} ({class_info}{self.class_assignment})"

    @property
    def is_space_created(self):
        """Check if ZEP space has been created for this student."""
        return bool(self.zep_space_url) or self.spaces.exists()

    @property
    def primary_space(self):
        """Get the primary space or the first available space."""
        # First check the new spaces model
        space = self.spaces.filter(is_primary=True).first()
        if space:
            return space
        # Fall back to first space
        space = self.spaces.first()
        if space:
            return space
        # Fall back to legacy zep_space_url
        if self.zep_space_url:
            return {'url': self.zep_space_url, 'name': '기본 스페이스'}
        return None

    @property
    def space_count(self):
        """Get total number of spaces including legacy field."""
        count = self.spaces.count()
        if not count and self.zep_space_url:
            return 1
        return count


class FailedSpaceCreation(models.Model):
    """
    Track failed ZEP space creation attempts for manual review

    When automated space creation fails, record is created here
    for administrator to review and retry manually
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='failed_space_attempts',
        verbose_name='학생'
    )
    error_message = models.TextField(
        verbose_name='오류 메시지',
        help_text='공간 생성 실패 시 오류 메시지'
    )
    retry_count = models.IntegerField(
        default=0,
        verbose_name='재시도 횟수'
    )
    last_attempted_at = models.DateTimeField(
        auto_now=True,
        verbose_name='마지막 시도 시각'
    )
    resolved = models.BooleanField(
        default=False,
        verbose_name='해결 여부'
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='해결 시각'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )

    class Meta:
        verbose_name = '스페이스 생성 실패'
        verbose_name_plural = '스페이스 생성 실패'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.error_message[:50]}"
