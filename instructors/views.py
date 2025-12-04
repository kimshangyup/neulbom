from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from authentication.decorators import admin_required, instructor_required
from .models import Instructor
from .forms import InstructorCreateForm, InstructorEditForm, ClassCreateForm
from students.models import School, Class
import logging

logger = logging.getLogger(__name__)


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
    from authentication.models import User

    # Try to find by Instructor.pk first, then by User.id
    try:
        instructor = Instructor.objects.get(pk=pk)
    except Instructor.DoesNotExist:
        # Try to find by User.id
        user = get_object_or_404(User, pk=pk, role='instructor')
        # Get or create Instructor profile
        instructor, created = Instructor.objects.get_or_create(
            user=user,
            defaults={'affiliated_school': user.affiliated_school}
        )

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
    from authentication.models import User

    # Try to find by Instructor.pk first, then by User.id
    try:
        instructor = Instructor.objects.get(pk=pk)
    except Instructor.DoesNotExist:
        # Try to find by User.id
        user = get_object_or_404(User, pk=pk, role='instructor')
        # Get or create Instructor profile
        instructor, created = Instructor.objects.get_or_create(
            user=user,
            defaults={'affiliated_school': user.affiliated_school}
        )

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
                return redirect('instructors:detail', pk=instructor.user.id)
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
def my_profile(request):
    """
    강사 본인 프로필 조회 및 수정

    강사가 자신의 소속학교 등 프로필 정보를 설정할 수 있습니다.
    """
    from authentication.models import User

    # Get or create Instructor profile for current user
    instructor, created = Instructor.objects.get_or_create(
        user=request.user,
        defaults={'affiliated_school': request.user.affiliated_school}
    )

    if request.method == 'POST':
        form = InstructorEditForm(request.POST, instance=instructor)
        if form.is_valid():
            try:
                instructor = form.save()
                logger.info(f"Instructor {instructor.user.username} updated their profile")
                messages.success(request, '프로필이 수정되었습니다.')
                return redirect('instructors:my_profile')
            except Exception as e:
                logger.error(f"Error updating instructor profile: {e}")
                messages.error(request, f'프로필 수정 중 오류가 발생했습니다: {e}')
        else:
            messages.error(request, '입력한 정보를 확인해주세요.')
    else:
        form = InstructorEditForm(instance=instructor)

    # Get instructor's classes
    classes = request.user.taught_classes.select_related('school').all()

    context = {
        'form': form,
        'instructor': instructor,
        'classes': classes,
        'title': '내 프로필',
        'submit_text': '저장',
    }

    return render(request, 'instructors/my_profile.html', context)


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
                return redirect('dashboard:instructor_dashboard')
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
