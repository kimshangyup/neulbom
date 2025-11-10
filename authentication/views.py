from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


def login_view(request):
    """
    Handle user login with ID/PW authentication

    Displays login form and processes authentication.
    On success, redirects to admin dashboard or appropriate page.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, '아이디와 비밀번호를 모두 입력해주세요.')
            return render(request, 'authentication/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"User {username} logged in successfully")
            messages.success(request, '로그인되었습니다.')

            # Redirect to appropriate page based on role
            next_url = request.GET.get('next')
            if not next_url:
                # Default redirect based on user role/permissions
                if user.is_staff or user.is_superuser or user.role == 'admin':
                    next_url = '/dashboard/admin/'
                elif user.role == 'instructor':
                    next_url = '/dashboard/instructor/'
                else:
                    next_url = '/'
            return redirect(next_url)
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')

    return render(request, 'authentication/login.html')


def logout_view(request):
    """
    Handle user logout

    Clears session and redirects to login page.
    """
    username = request.user.username if request.user.is_authenticated else 'Anonymous'
    logout(request)
    logger.info(f"User {username} logged out")
    messages.success(request, '로그아웃되었습니다.')
    return redirect('authentication:login')


def register_view(request):
    """
    Handle instructor registration

    Creates new instructor account with User and Instructor profile.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        # Validation
        if not all([username, password, password_confirm, first_name, last_name]):
            messages.error(request, '필수 항목을 모두 입력해주세요.')
            return render(request, 'authentication/register.html')

        if password != password_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, 'authentication/register.html')

        if len(password) < 8:
            messages.error(request, '비밀번호는 8자 이상이어야 합니다.')
            return render(request, 'authentication/register.html')

        # Check if username already exists
        from authentication.models import User
        if User.objects.filter(username=username).exists():
            messages.error(request, '이미 사용 중인 아이디입니다.')
            return render(request, 'authentication/register.html')

        # Create user and instructor profile
        try:
            with transaction.atomic():
                from instructors.models import Instructor

                # Create User
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    role='instructor'
                )

                # Create Instructor profile
                Instructor.objects.create(
                    user=user,
                    training_completed=False
                )

                logger.info(f"New instructor registered: {username}")
                messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.')
                return redirect('authentication:login')

        except Exception as e:
            logger.error(f"Registration failed for {username}: {str(e)}")
            messages.error(request, '회원가입 중 오류가 발생했습니다. 다시 시도해주세요.')
            return render(request, 'authentication/register.html')

    return render(request, 'authentication/register.html')
