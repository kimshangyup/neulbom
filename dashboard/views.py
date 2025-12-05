from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from authentication.mixins import admin_required, instructor_required
from authentication.models import User
from students.models import Student
from dashboard.metrics import DashboardMetrics
from dashboard.export import export_metrics_csv, export_students_csv

@admin_required
def admin_dashboard(request):
    """
    Main administrator dashboard view with hierarchical data.
    Displays instructors -> schools -> classes -> students with ZEP links.
    """
    from students.models import Class, School
    import json

    metrics = DashboardMetrics.get_core_metrics()

    # Get hierarchical instructor data
    instructors = User.objects.filter(role='instructor').select_related(
        'affiliated_school'
    ).prefetch_related(
        'taught_classes__students',
        'taught_classes__school'
    ).order_by('affiliated_school__name', 'last_name', 'first_name')

    # Structure data hierarchically
    instructor_data = []
    for instructor in instructors:
        classes_data = []
        # Only show classes that have an instructor assigned (taught_classes already filters by instructor)
        for cls in instructor.taught_classes.filter(instructor__isnull=False):
            students = cls.students.all()
            classes_data.append({
                'id': cls.id,
                'name': cls.name,
                'school': cls.school.name if cls.school else 'N/A',
                'student_count': students.count(),
                'students': students
            })

        instructor_data.append({
            'id': instructor.id,
            'username': instructor.username,
            'full_name': instructor.get_full_name() or instructor.username,
            'email': instructor.email,
            'school': instructor.affiliated_school.name if instructor.affiliated_school else 'N/A',
            'last_login': instructor.last_login,
            'class_count': len(classes_data),
            'student_count': sum(c['student_count'] for c in classes_data),
            'classes': classes_data
        })

    # Prepare chart data
    schools = School.objects.all().order_by('name')
    school_names = []
    students_per_school = []
    instructors_per_school = []
    classes_per_school = []

    for school in schools:
        school_names.append(school.name)

        # Count students per school (only in classes with instructors)
        student_count = Student.objects.filter(
            class_assignment__school=school,
            class_assignment__instructor__isnull=False
        ).count()
        students_per_school.append(student_count)

        # Count instructors per school
        instructor_count = User.objects.filter(role='instructor', affiliated_school=school).count()
        instructors_per_school.append(instructor_count)

        # Count classes per school (only classes with instructors)
        class_count = Class.objects.filter(
            school=school,
            instructor__isnull=False
        ).count()
        classes_per_school.append(class_count)

    chart_data = {
        'school_names': json.dumps(school_names),
        'students_per_school': json.dumps(students_per_school),
        'instructors_per_school': json.dumps(instructors_per_school),
        'classes_per_school': json.dumps(classes_per_school),
    }

    # Get school data for school management section
    school_data = []
    for school in schools:
        # Count instructors assigned to this school
        instructor_count = User.objects.filter(
            role='instructor',
            affiliated_school=school
        ).count()

        # Count all classes (not just those with instructors)
        class_count = Class.objects.filter(school=school).count()

        # Count all students
        student_count = Student.objects.filter(
            class_assignment__school=school
        ).count()

        # Get instructors list
        school_instructors = User.objects.filter(
            role='instructor',
            affiliated_school=school
        ).values_list('first_name', 'last_name', 'username')

        instructor_names = [
            f"{fn} {ln}".strip() or un
            for fn, ln, un in school_instructors
        ]

        school_data.append({
            'id': school.id,
            'name': school.name,
            'notes': school.notes,
            'instructor_count': instructor_count,
            'class_count': class_count,
            'student_count': student_count,
            'instructor_names': instructor_names,
            'created_at': school.created_at,
        })

    context = {
        'metrics': metrics,
        'instructors': instructor_data,
        'schools': school_data,
        'chart_data': chart_data,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@admin_required
def metrics_api(request):
    """
    JSON API endpoint for real-time metrics updates.
    Used by AJAX polling to refresh dashboard without page reload.
    """
    metrics = DashboardMetrics.get_core_metrics()
    instructor_activity = DashboardMetrics.get_instructor_activity()

    # Combine metrics with instructor activity for API response
    response_data = {**metrics}
    response_data['instructor_activity'] = instructor_activity

    return JsonResponse(response_data, safe=False)

@admin_required
def export_metrics(request):
    """
    Export dashboard metrics as CSV file with UTF-8 BOM for Excel compatibility.
    """
    metrics = DashboardMetrics.get_core_metrics()
    return export_metrics_csv(metrics)

@admin_required
def instructor_detail(request, instructor_id):
    """
    Detailed view of individual instructor activity and statistics.

    Displays:
    - Basic instructor information
    - Classes taught with student counts
    - Space creation statistics
    - Recent activity timeline
    """
    from django.utils import timezone
    from datetime import timedelta

    # Get instructor with related data
    instructor = get_object_or_404(
        User.objects.select_related('affiliated_school'),
        id=instructor_id,
        role='instructor'
    )

    # Get classes with student counts
    classes = instructor.taught_classes.annotate(
        student_count=Count('students'),
        spaces_created=Count(
            'students',
            filter=~Q(students__zep_space_url=''),
            distinct=True
        )
    ).order_by('-created_at')

    # Calculate statistics
    thirty_days_ago = timezone.now() - timedelta(days=30)
    total_students = sum(cls.student_count for cls in classes)
    total_spaces = sum(cls.spaces_created for cls in classes)
    is_inactive = not instructor.last_login or instructor.last_login < thirty_days_ago

    # Recent activity timeline (simplified - can be enhanced)
    recent_activity = []
    if instructor.last_login:
        recent_activity.append({
            'timestamp': instructor.last_login,
            'action': '로그인',
            'description': '시스템에 로그인했습니다.'
        })

    context = {
        'instructor': instructor,
        'classes': classes,
        'total_classes': classes.count(),
        'total_students': total_students,
        'total_spaces': total_spaces,
        'is_inactive': is_inactive,
        'recent_activity': recent_activity,
    }

    return render(request, 'dashboard/instructor_detail.html', context)

@instructor_required
def get_schools(request):
    """
    API endpoint to get schools created by the logged-in instructor for dropdown.
    Also includes schools without an assigned instructor (legacy data).
    """
    from students.models import School
    from django.db.models import Q
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Return schools created by this instructor OR schools without an instructor (legacy)
        schools = School.objects.filter(
            Q(instructor=request.user) | Q(instructor__isnull=True)
        ).order_by('name')
        schools_data = [{'id': school.id, 'name': school.name} for school in schools]

        logger.info(f"User {request.user.username} has {len(schools_data)} schools")

        return JsonResponse({'success': True, 'schools': schools_data})
    except Exception as e:
        logger.error(f"Error in get_schools: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@instructor_required
def instructor_dashboard(request):
    """
    Instructor dashboard with hierarchical class and student view.
    Displays schools -> classes -> students with ZEP links.
    Shows schools created by the logged-in instructor or legacy schools without an instructor.
    """
    from students.models import School
    from django.db.models import Q

    instructor = request.user

    # Get instructor's classes with students
    classes = instructor.taught_classes.all().select_related(
        'school'
    ).prefetch_related('students').order_by('school__name', 'name')

    # Get schools created by this instructor (including those without classes)
    instructor_schools = School.objects.filter(
        Q(instructor=instructor) | Q(instructor__isnull=True)
    ).order_by('name')

    # Structure data hierarchically by school
    schools_data = {}

    # First, add all instructor's schools (even if they have no classes yet)
    for school in instructor_schools:
        schools_data[school.name] = []

    # Populate with classes
    for cls in classes:
        school_name = cls.school.name if cls.school else '소속 없음'
        if school_name not in schools_data:
            schools_data[school_name] = []

        students = cls.students.all()
        schools_data[school_name].append({
            'id': cls.id,
            'name': cls.name,
            'academic_year': cls.academic_year,
            'semester_display': cls.get_semester_display(),
            'student_count': students.count(),
            'spaces_created': students.exclude(zep_space_url='').count(),
            'students': students
        })

    # Calculate summary statistics
    total_classes = classes.count()
    total_students = sum(
        cls['student_count']
        for school in schools_data.values()
        for cls in school
    )
    total_spaces = sum(
        cls['spaces_created']
        for school in schools_data.values()
        for cls in school
    )

    context = {
        'schools': schools_data,
        'total_classes': total_classes,
        'total_students': total_students,
        'total_spaces': total_spaces,
    }

    return render(request, 'dashboard/instructor_dashboard.html', context)

@instructor_required
def create_school(request):
    """
    API endpoint to create a new school.
    Only requires name and notes (optional).
    Automatically assigns the logged-in instructor as the school owner.
    """
    if request.method == 'POST':
        import json
        from students.models import School

        try:
            data = json.loads(request.body)
            school_name = data['name'].strip()

            # Validate school name length (max 10 characters)
            if len(school_name) > 10:
                return JsonResponse({
                    'success': False,
                    'error': '학교명은 10글자 이내로 입력해주세요.'
                }, status=400)

            if len(school_name) == 0:
                return JsonResponse({
                    'success': False,
                    'error': '학교명을 입력해주세요.'
                }, status=400)

            # Check if school with this name already exists
            if School.objects.filter(name=school_name).exists():
                return JsonResponse({
                    'success': False,
                    'error': '이미 존재하는 학교 이름입니다.'
                }, status=400)

            school = School.objects.create(
                name=school_name,
                notes=data.get('notes', ''),
                instructor=request.user  # Assign current instructor
            )
            return JsonResponse({
                'success': True,
                'school': {
                    'id': school.id,
                    'name': school.name
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@instructor_required
def create_class(request):
    """
    API endpoint to create a new class.
    """
    if request.method == 'POST':
        import json
        from students.models import School, Class
        from datetime import datetime

        try:
            data = json.loads(request.body)
            instructor = request.user

            school = School.objects.get(id=data['school_id'])
            class_obj = Class.objects.create(
                name=data['name'],
                school=school,
                instructor=instructor,
                academic_year=data.get('academic_year', datetime.now().year),
                semester=data.get('semester', 'spring')
            )
            return JsonResponse({
                'success': True,
                'class': {
                    'id': class_obj.id,
                    'name': class_obj.name,
                    'school': school.name
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@instructor_required
def create_student(request):
    """
    API endpoint to create a new student.
    """
    if request.method == 'POST':
        import json
        from students.models import Class, Student

        try:
            data = json.loads(request.body)

            # Validate student name length
            student_name = data.get('name', '').strip()
            if len(student_name) > 10:
                return JsonResponse({
                    'success': False,
                    'error': '학생 이름은 10글자 이내로 입력해주세요.'
                }, status=400)

            if len(student_name) == 0:
                return JsonResponse({
                    'success': False,
                    'error': '학생 이름을 입력해주세요.'
                }, status=400)

            class_obj = Class.objects.get(id=data['class_id'])

            # Verify instructor owns this class
            if class_obj.instructor != request.user:
                return JsonResponse({'success': False, 'error': '권한이 없습니다'}, status=403)

            # Create user account for the student
            from students.services import StudentAccountService, generate_password
            username, generated_email = StudentAccountService.generate_student_username(
                data['name'],
                class_obj.school.name,
                class_obj.name
            )
            password = generate_password()

            user = User.objects.create_user(
                username=username,
                email=generated_email,
                password=password,
                role='student',
                first_name=data['name'],
                affiliated_school=class_obj.school
            )

            student = Student.objects.create(
                user=user,
                name=data['name'],
                class_number=data.get('class_number'),
                grade=data.get('grade'),
                class_assignment=class_obj,
                generated_email=generated_email
            )

            return JsonResponse({
                'success': True,
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'class_number': student.class_number,
                    'grade': student.grade,
                    'class': class_obj.name,
                    'space_count': student.space_count,
                    'is_space_created': student.is_space_created
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@instructor_required
def update_student(request, student_id):
    """
    API endpoint to update student information.
    Only the instructor who owns the class can update the student.
    """
    if request.method == 'PUT':
        import json

        try:
            data = json.loads(request.body)

            # Validate student name length
            student_name = data.get('name', '').strip()
            if student_name and len(student_name) > 10:
                return JsonResponse({
                    'success': False,
                    'error': '학생 이름은 10글자 이내로 입력해주세요.'
                }, status=400)

            # Get the student and verify instructor owns the class
            student = Student.objects.select_related('class_assignment').get(id=student_id)

            if student.class_assignment.instructor != request.user:
                return JsonResponse({'success': False, 'error': '권한이 없습니다'}, status=403)

            # Update student fields
            student.name = student_name if student_name else student.name
            student.class_number = data.get('class_number')
            student.grade = data.get('grade')
            student.zep_space_url = data.get('zep_space_url', '')
            student.save()

            return JsonResponse({
                'success': True,
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'class_number': student.class_number,
                    'grade': student.grade,
                    'zep_space_url': student.zep_space_url,
                    'is_space_created': student.is_space_created
                }
            })
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': '학생을 찾을 수 없습니다'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@instructor_required
def add_student_space(request, student_id):
    """
    API endpoint to add a new ZEP space to a student.
    Allows multiple spaces per student.
    """
    if request.method == 'POST':
        import json
        from spaces.models import StudentSpace

        try:
            data = json.loads(request.body)

            # Get the student and verify instructor owns the class
            student = Student.objects.select_related('class_assignment').get(id=student_id)

            if student.class_assignment.instructor != request.user:
                return JsonResponse({'success': False, 'error': '권한이 없습니다'}, status=403)

            # Migrate legacy zep_space_url to StudentSpace if exists and not yet migrated
            if student.zep_space_url and not student.spaces.exists():
                StudentSpace.objects.create(
                    student=student,
                    name='기본 스페이스',
                    url=student.zep_space_url,
                    is_primary=True,
                    is_public=student.is_public,
                    description='기존 스페이스 (자동 마이그레이션)'
                )

            # Check if this is the first space (after migration check)
            is_first = not student.spaces.exists()

            # Create new space
            space = StudentSpace.objects.create(
                student=student,
                name=data.get('name', '기본 스페이스'),
                url=data['url'],
                is_primary=is_first or data.get('is_primary', False),
                is_public=data.get('is_public', False),
                description=data.get('description', '')
            )

            return JsonResponse({
                'success': True,
                'space': {
                    'id': space.id,
                    'name': space.name,
                    'url': space.url,
                    'is_primary': space.is_primary,
                    'is_public': space.is_public
                }
            })
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': '학생을 찾을 수 없습니다'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@instructor_required
def get_student_spaces(request, student_id):
    """
    API endpoint to get all spaces for a student.
    """
    try:
        student = Student.objects.select_related('class_assignment').get(id=student_id)

        if student.class_assignment.instructor != request.user:
            return JsonResponse({'success': False, 'error': '권한이 없습니다'}, status=403)

        spaces = []

        # Get spaces from new model
        for space in student.spaces.all():
            spaces.append({
                'id': space.id,
                'name': space.name,
                'url': space.url,
                'is_primary': space.is_primary,
                'is_public': space.is_public
            })

        # Include legacy zep_space_url if no new spaces exist
        if not spaces and student.zep_space_url:
            spaces.append({
                'id': None,
                'name': '기본 스페이스',
                'url': student.zep_space_url,
                'is_primary': True,
                'is_public': student.is_public,
                'legacy': True
            })

        return JsonResponse({
            'success': True,
            'student_id': student.id,
            'student_name': student.name,
            'spaces': spaces
        })
    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'error': '학생을 찾을 수 없습니다'}, status=404)


@instructor_required
def delete_student_space(request, space_id):
    """
    API endpoint to delete a student space.
    """
    if request.method == 'DELETE':
        from spaces.models import StudentSpace

        try:
            space = StudentSpace.objects.select_related(
                'student__class_assignment'
            ).get(id=space_id)

            if space.student.class_assignment.instructor != request.user:
                return JsonResponse({'success': False, 'error': '권한이 없습니다'}, status=403)

            space.delete()

            return JsonResponse({'success': True})
        except StudentSpace.DoesNotExist:
            return JsonResponse({'success': False, 'error': '스페이스를 찾을 수 없습니다'}, status=404)

    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@instructor_required
def export_students(request):
    """
    Export instructor's students as CSV file with UTF-8 BOM for Excel compatibility.
    Respects filters applied in the dashboard (class filter and name search).
    """
    instructor = request.user

    # Get all students from instructor's classes
    students_query = Student.objects.filter(
        class_assignment__instructor=instructor
    ).select_related('class_assignment', 'class_assignment__school', 'user').order_by(
        'class_assignment__name', 'name'
    )

    # Apply same filters as dashboard
    class_id = request.GET.get('class')
    if class_id:
        try:
            students_query = students_query.filter(class_assignment_id=int(class_id))
        except (ValueError, TypeError):
            pass

    search_query = request.GET.get('search', '').strip()
    if search_query:
        students_query = students_query.filter(name__icontains=search_query)

    return export_students_csv(students_query)
