from django import forms
from django.contrib.auth import get_user_model
from .models import Instructor
from students.models import School, Class

User = get_user_model()


class InstructorCreateForm(forms.ModelForm):
    """Form for creating new instructor account."""
    username = forms.CharField(
        max_length=150,
        label='사용자명',
        help_text='강사 계정의 사용자명'
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='비밀번호',
        help_text='강사 계정의 비밀번호'
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label='이름'
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label='성'
    )
    affiliated_school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        required=False,
        label='소속 학교',
        empty_label='학교 선택'
    )
    training_completed = forms.BooleanField(
        required=False,
        label='연수 완료',
        help_text='강사 연수 이수 여부'
    )

    class Meta:
        model = Instructor
        fields = ['affiliated_school', 'training_completed']

    def clean_username(self):
        """Validate that username is unique."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('이미 존재하는 사용자 이름입니다.')
        return username

    def save(self, commit=True):
        """Create User and Instructor profile."""
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data.get('first_name', ''),
            last_name=self.cleaned_data.get('last_name', ''),
            role='instructor'
        )

        instructor = super().save(commit=False)
        instructor.user = user

        if commit:
            instructor.save()

        return instructor


class InstructorEditForm(forms.ModelForm):
    """Form for editing instructor profile information."""
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label='이름'
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label='성'
    )
    affiliated_school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        required=False,
        label='소속 학교',
        empty_label='학교 선택'
    )
    training_completed = forms.BooleanField(
        required=False,
        label='연수 완료'
    )

    class Meta:
        model = Instructor
        fields = ['affiliated_school', 'training_completed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        """Update both Instructor and User information."""
        instructor = super().save(commit=False)

        # Update user information
        user = instructor.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')

        if commit:
            user.save()
            instructor.save()

        return instructor


class ClassCreateForm(forms.ModelForm):
    """간단한 학급 생성 폼 (학급명만 입력)"""
    name = forms.CharField(
        max_length=100,
        label='학급명',
        help_text='예: 1학년 A반',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '1학년 A반'
        })
    )

    class Meta:
        model = Class
        fields = ['name']

    def __init__(self, *args, instructor=None, **kwargs):
        """
        Initialize form with instructor context

        Args:
            instructor: User object of the instructor creating the class
        """
        super().__init__(*args, **kwargs)
        self.instructor = instructor

    def save(self, commit=True):
        """Create class with instructor and default values"""
        class_obj = super().save(commit=False)

        # Set instructor
        class_obj.instructor = self.instructor

        # Set school from instructor's affiliated_school (if exists)
        if hasattr(self.instructor, 'instructor') and self.instructor.instructor.affiliated_school:
            class_obj.school = self.instructor.instructor.affiliated_school
        else:
            # Create default school if instructor has no school
            from datetime import datetime
            default_school, _ = School.objects.get_or_create(
                name='기본 학교',
                defaults={
                    'address': '',
                    'contact_email': '',
                    'contact_phone': ''
                }
            )
            class_obj.school = default_school

        # Set default academic year and semester
        from datetime import datetime
        current_year = datetime.now().year
        current_month = datetime.now().month

        class_obj.academic_year = current_year
        class_obj.semester = 'spring' if current_month <= 6 else 'fall'

        if commit:
            class_obj.save()

        return class_obj
