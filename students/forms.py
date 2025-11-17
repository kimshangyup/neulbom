from django import forms
from .models import Student


class StudentSpaceForm(forms.ModelForm):
    """
    Form for editing student ZEP space URL and public visibility
    """
    class Meta:
        model = Student
        fields = ['zep_space_url', 'is_public']
        widgets = {
            'zep_space_url': forms.URLInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'https://zep.us/play/...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'
            }),
        }
        labels = {
            'zep_space_url': 'ZEP 스페이스 URL',
            'is_public': '공개 설정',
        }
        help_texts = {
            'is_public': '체크하면 랜딩 페이지에서 이 스페이스가 공개됩니다.',
        }


class StudentUploadForm(forms.Form):
    """
    Form for uploading student roster CSV/Excel file

    CSV should include: school_name, class_name, student_name, class_number (optional), grade (optional)
    Schools and classes will be auto-created if they don't exist.
    """
    file = forms.FileField(
        label='학생 명단 파일',
        help_text='CSV 파일에는 school_name, class_name, student_name 열이 필수입니다. class_number, grade, zep_space_url은 선택입니다.',
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none',
            'accept': '.csv,.xlsx,.xls'
        })
    )

    def __init__(self, *args, **kwargs):
        instructor = kwargs.pop('instructor', None)
        super().__init__(*args, **kwargs)
        self.instructor = instructor

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if not file:
            raise forms.ValidationError('파일을 선택해주세요.')

        # Check file extension
        filename = file.name.lower()
        if not (filename.endswith('.csv') or filename.endswith('.xlsx') or filename.endswith('.xls')):
            raise forms.ValidationError('CSV 또는 Excel 파일만 업로드 가능합니다.')

        # Check file size (limit to 5MB)
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('파일 크기는 5MB를 초과할 수 없습니다.')

        return file

    def parse_csv(self):
        """
        Parse uploaded CSV file and return list of student data.

        Uses CSVValidator for comprehensive validation with pandas.

        Returns:
            list: List of dicts with student information
        """
        from .validators import CSVValidator

        file = self.cleaned_data.get('file')
        validator = CSVValidator()
        result = validator.validate(file)

        if not result['valid']:
            # Join all errors with newlines for better display
            error_message = '\n'.join(result['errors'])
            raise forms.ValidationError(error_message)

        return result['data']
