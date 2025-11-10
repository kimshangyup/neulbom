from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access control

    Extends Django's AbstractUser to add role differentiation
    for administrators, instructors, and students.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text='User role determines access permissions'
    )
    affiliated_school = models.ForeignKey(
        'students.School',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users',
        help_text='School affiliation for instructors and students'
    )
    training_completed = models.BooleanField(
        default=False,
        help_text='Indicates if instructor has completed training'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
