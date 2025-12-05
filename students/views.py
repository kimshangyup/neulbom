from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from authentication.decorators import instructor_required
from .models import Student, Class
from .forms import StudentUploadForm, StudentSpaceForm
import csv
import logging

logger = logging.getLogger(__name__)


@instructor_required
def student_list(request):
    """
    Display list of all students for the instructor

    Instructors can view students in their classes with search functionality
    """
    # Get all students in classes taught by this instructor
    students = Student.objects.filter(
        class_assignment__instructor=request.user
    ).select_related('user', 'class_assignment', 'class_assignment__school')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(generated_email__icontains=search_query)
        )

    # Filter by class
    class_id = request.GET.get('class')
    if class_id:
        students = students.filter(class_assignment_id=class_id)

    # Get list of classes for filter dropdown
    classes = Class.objects.filter(instructor=request.user).select_related('school')

    context = {
        'students': students,
        'classes': classes,
        'search_query': search_query,
        'selected_class': class_id,
    }

    return render(request, 'students/student_list.html', context)


@instructor_required
def student_upload(request):
    """
    Handle student roster CSV/Excel file upload

    Displays upload form and preview of students to be created
    """
    if request.method == 'POST':
        if 'preview' in request.POST:
            # Step 1: Parse file and show preview
            form = StudentUploadForm(request.POST, request.FILES, instructor=request.user)

            if form.is_valid():
                try:
                    students_data = form.parse_csv()

                    # Check for duplicates
                    from students.models import School, Class
                    from collections import defaultdict

                    # Group by school/class and check duplicates
                    for student in students_data:
                        school_name = student.get('school_name')
                        class_name = student.get('class_name')
                        name = student.get('student_name')

                        # Check if school and class exist
                        school = School.objects.filter(name=school_name).first()
                        if school:
                            class_obj = Class.objects.filter(
                                name=class_name,
                                school=school,
                                instructor=request.user
                            ).first()

                            if class_obj:
                                # Check if student already exists
                                from students.models import Student
                                existing = Student.objects.filter(
                                    name=name,
                                    class_assignment=class_obj
                                ).first()

                                if existing:
                                    student['is_duplicate'] = True
                                    student['duplicate_warning'] = f'{name}은(는) 이미 {school_name} {class_name}에 등록되어 있습니다.'
                                else:
                                    student['is_duplicate'] = False
                            else:
                                student['is_duplicate'] = False
                        else:
                            student['is_duplicate'] = False

                    # Store data in session for confirmation step
                    request.session['upload_data'] = {
                        'students': students_data,
                    }

                    context = {
                        'students_data': students_data,
                        'preview_mode': True,
                    }

                    return render(request, 'students/student_upload_preview.html', context)

                except Exception as e:
                    logger.error(f"Error parsing file: {e}")
                    messages.error(request, f'파일 처리 중 오류가 발생했습니다: {e}')

        elif 'confirm' in request.POST:
            # Step 2: Confirm and create students with auto school/class creation
            upload_data = request.session.get('upload_data')

            if not upload_data:
                messages.error(request, '업로드 데이터를 찾을 수 없습니다. 다시 시도해주세요.')
                return redirect('students:upload-csv')

            try:
                from .services import create_students_from_csv_with_auto_school_class, get_student_credentials

                students_data = upload_data['students']

                # Get selected students from checkboxes (exclude duplicates if unchecked)
                selected_indices = request.POST.getlist('selected_students')
                if selected_indices:
                    # Filter to only include selected students
                    selected_indices = [int(idx) for idx in selected_indices]
                    students_data = [students_data[idx] for idx in selected_indices if idx < len(students_data)]

                # Create student accounts with auto school/class creation
                created_students, creation_results = create_students_from_csv_with_auto_school_class(
                    students_data=students_data,
                    instructor_user=request.user
                )

                # Store credentials in session for display
                credentials = get_student_credentials(creation_results)
                request.session['student_credentials'] = credentials

                # Count successes and failures
                success_count = len([r for r in creation_results if r['success']])
                failure_count = len([r for r in creation_results if not r['success']])

                if success_count > 0:
                    messages.success(
                        request,
                        f'{success_count}명의 학생 계정이 생성되었습니다.'
                    )

                if failure_count > 0:
                    messages.warning(
                        request,
                        f'{failure_count}명의 학생 계정 생성에 실패했습니다.'
                    )

                # Create ZEP spaces for students who don't already have a space URL
                students_without_space = [s for s in created_students if not s.zep_space_url]
                students_with_space = len(created_students) - len(students_without_space)

                if students_with_space > 0:
                    messages.info(
                        request,
                        f'{students_with_space}명의 학생은 이미 ZEP 스페이스 URL이 등록되어 있습니다.'
                    )

                # Skip ZEP space creation for large batches to avoid timeout
                MAX_BATCH_SIZE_FOR_AUTO_SPACE = 30

                if students_without_space:
                    if len(students_without_space) > MAX_BATCH_SIZE_FOR_AUTO_SPACE:
                        # Too many students - skip auto ZEP creation
                        messages.warning(
                            request,
                            f'{len(students_without_space)}명의 학생 계정이 생성되었습니다. '
                            f'학생 수가 많아 ZEP 스페이스 자동 생성이 생략되었습니다. '
                            f'대시보드에서 개별 학생의 스페이스를 추가해주세요.'
                        )
                    else:
                        from spaces.services import create_spaces_for_students, get_admin_emails

                        instructor_email = request.user.email
                        admin_emails = get_admin_emails()

                        space_results = create_spaces_for_students(
                            students=students_without_space,
                            instructor_email=instructor_email,
                            admin_emails=admin_emails
                        )

                        if space_results['success'] > 0:
                            messages.success(
                                request,
                                f'{space_results["success"]}개의 ZEP 스페이스가 생성되었습니다.'
                            )

                        if space_results['failed'] > 0:
                            messages.warning(
                                request,
                                f'{space_results["failed"]}개의 ZEP 스페이스 생성에 실패했습니다. '
                                f'관리자 페이지에서 확인하세요.'
                            )

                # Clean up session
                del request.session['upload_data']

                # Redirect to instructor dashboard
                return redirect('dashboard:instructor_dashboard')

            except Exception as e:
                logger.error(f"Error creating student accounts: {e}")
                messages.error(request, f'학생 계정 생성 중 오류가 발생했습니다: {e}')
                return redirect('students:upload-csv')

    else:
        form = StudentUploadForm(instructor=request.user)

    context = {
        'form': form,
    }

    return render(request, 'students/student_upload.html', context)


@instructor_required
def student_credentials(request):
    """
    Display created student credentials

    Shows username and password for newly created students
    Allows downloading as CSV
    """
    credentials = request.session.get('student_credentials', [])

    if not credentials:
        messages.info(request, '표시할 계정 정보가 없습니다.')
        return redirect('students:list')

    context = {
        'credentials': credentials,
    }

    return render(request, 'students/student_credentials.html', context)


@instructor_required
def download_credentials(request):
    """
    Download student credentials as CSV file
    """
    credentials = request.session.get('student_credentials', [])

    if not credentials:
        messages.error(request, '다운로드할 계정 정보가 없습니다.')
        return redirect('students:list')

    from .services import export_credentials_csv

    csv_content = export_credentials_csv(credentials)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="student_credentials.csv"'
    response.write('\ufeff')  # BOM for Excel UTF-8 recognition
    response.write(csv_content)

    logger.info(f"Credentials downloaded by {request.user.username}")

    return response


@instructor_required
def student_edit_space(request, pk):
    """
    Edit student ZEP space URL

    Instructors can manually edit or add ZEP space URLs
    """
    from django.shortcuts import get_object_or_404

    student = get_object_or_404(
        Student,
        pk=pk,
        class_assignment__instructor=request.user
    )

    if request.method == 'POST':
        form = StudentSpaceForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'{student.name}의 ZEP 스페이스 URL이 업데이트되었습니다.')
            return redirect('students:list')
    else:
        form = StudentSpaceForm(instance=student)

    context = {
        'form': form,
        'student': student,
    }

    return render(request, 'students/student_edit_space.html', context)


@instructor_required
def download_template(request):
    """
    Download CSV template for student roster

    Returns CSV file with required columns: school_name, class_name, student_name, class_number, grade, zep_space_url
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="student_template.csv"'

    # Add BOM for Excel to recognize UTF-8
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['school_name', 'class_name', 'student_name', 'class_number', 'grade', 'zep_space_url'])
    writer.writerow(['서울초등학교', '1학년 A반', '홍길동', '1', '1', 'https://zep.us/play/example1'])
    writer.writerow(['서울초등학교', '1학년 A반', '김철수', '2', '1', 'https://zep.us/play/example2'])
    writer.writerow(['서울초등학교', '2학년 B반', '이영희', '1', '2', ''])

    logger.info(f"Template downloaded by {request.user.username}")

    return response
