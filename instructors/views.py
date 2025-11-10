from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from authentication.decorators import admin_required, instructor_required
from .models import Instructor
from .forms import InstructorCreateForm, InstructorEditForm, ClassCreateForm
from students.models import School, Class
import logging

logger = logging.getLogger(__name__)


@instructor_required
def instructor_dashboard(request):
    """
    Instructor dashboard with Student Management section.

    Displays instructor's classes and provides navigation to student management features.
    """
    # Get instructor's classes
    classes = Class.objects.filter(
        instructor=request.user
    ).select_related('school').prefetch_related('students')

    # Calculate statistics
    total_classes = classes.count()
    total_students = sum(c.student_count() for c in classes)

    context = {
        'classes': classes,
        'total_classes': total_classes,
        'total_students': total_students,
    }

    return render(request, 'instructors/dashboard.html', context)


@admin_required
def instructor_list(request):
    """
    Display list of all instructors with search and filter capabilities.

    Supports search by name/username and filter by school and training status.
    """
    instructors = Instructor.objects.select_related(
        'user', 'affiliated_school'
    )

    # Search by instructor name
    search_query = request.GET.get('search', '')
    if search_query:
        instructors = instructors.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )

    # Filter by school
    school_filter = request.GET.get('school', '')
    if school_filter:
        instructors = instructors.filter(affiliated_school_id=school_filter)

    # Filter by training status
    training_filter = request.GET.get('training', '')
    if training_filter == 'completed':
        instructors = instructors.filter(training_completed=True)
    elif training_filter == 'incomplete':
        instructors = instructors.filter(training_completed=False)

    context = {
        'instructors': instructors,
        'search_query': search_query,
        'school_filter': school_filter,
        'training_filter': training_filter,
        'schools': School.objects.all(),
    }

    return render(request, 'instructors/list.html', context)


@admin_required
def instructor_create(request):
    """Create new instructor account."""
    if request.method == 'POST':
        form = InstructorCreateForm(request.POST)
        if form.is_valid():
            try:
                instructor = form.save()
                logger.info(f"Instructor {instructor.user.username} created by {request.user.username}")
                messages.success(
                    request,
                    f'강사 "{instructor.user.get_full_name() or instructor.user.username}" 계정이 생성되었습니다.'
                )
                return redirect('instructors:detail', pk=instructor.pk)
            except Exception as e:
                logger.error(f"Error creating instructor: {e}")
                messages.error(request, f'강사 계정 생성 중 오류가 발생했습니다: {e}')
        else:
            messages.error(request, '입력한 정보를 확인해주세요.')
    else:
        form = InstructorCreateForm()

    context = {
        'form': form,
        'title': '새 강사 등록',
        'submit_text': '등록',
    }

    return render(request, 'instructors/create.html', context)


@admin_required
def instructor_detail(request, pk):
    """Display detailed information about an instructor."""
    instructor = get_object_or_404(Instructor, pk=pk)

    # Get instructor's classes
    classes = instructor.user.taught_classes.select_related('school').all()

    context = {
        'instructor': instructor,
        'classes': classes,
    }

    return render(request, 'instructors/detail.html', context)


@admin_required
def instructor_edit(request, pk):
    """Edit instructor profile information."""
    instructor = get_object_or_404(Instructor, pk=pk)

    if request.method == 'POST':
        form = InstructorEditForm(request.POST, instance=instructor)
        if form.is_valid():
            try:
                instructor = form.save()
                logger.info(f"Instructor {instructor.user.username} updated by {request.user.username}")
                messages.success(
                    request,
                    f'강사 "{instructor.user.get_full_name() or instructor.user.username}" 정보가 수정되었습니다.'
                )
                return redirect('instructors:detail', pk=instructor.pk)
            except Exception as e:
                logger.error(f"Error updating instructor: {e}")
                messages.error(request, f'강사 정보 수정 중 오류가 발생했습니다: {e}')
        else:
            messages.error(request, '입력한 정보를 확인해주세요.')
    else:
        form = InstructorEditForm(instance=instructor)

    context = {
        'form': form,
        'instructor': instructor,
        'title': '강사 정보 수정',
        'submit_text': '수정',
    }

    return render(request, 'instructors/edit.html', context)


@instructor_required
def class_create(request):
    """
    학급 생성 (강사용)

    강사가 자신의 학급을 생성합니다. 학급명만 입력하면 됩니다.
    """
    if request.method == 'POST':
        form = ClassCreateForm(request.POST, instructor=request.user)
        if form.is_valid():
            try:
                class_obj = form.save()
                logger.info(f"Class {class_obj.name} created by {request.user.username}")
                messages.success(
                    request,
                    f'학급 "{class_obj.name}"이(가) 생성되었습니다.'
                )
                return redirect('instructors:dashboard')
            except Exception as e:
                logger.error(f"Error creating class: {e}")
                messages.error(request, f'학급 생성 중 오류가 발생했습니다: {e}')
        else:
            messages.error(request, '입력한 정보를 확인해주세요.')
    else:
        form = ClassCreateForm(instructor=request.user)

    context = {
        'form': form,
    }

    return render(request, 'instructors/class_create.html', context)
