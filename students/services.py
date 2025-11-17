"""
Student management services

Business logic for bulk student creation and management
"""

from django.db import transaction
from django.contrib.auth import get_user_model
from typing import List, Dict, Tuple
import logging
import secrets
import string
import time
import pandas as pd

from .models import Student, Class, School, FailedSpaceCreation
from datetime import datetime

User = get_user_model()
logger = logging.getLogger(__name__)


class StudentCreationError(Exception):
    """Custom exception for student creation errors"""
    pass


def generate_password(length: int = 12) -> str:
    """
    Generate secure random password

    Args:
        length: Password length (default: 12)

    Returns:
        str: Random password
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


class StudentAccountService:
    """Service class for student account operations"""

    @staticmethod
    def generate_student_username(name: str, school_name: str, class_name: str) -> tuple:
        """
        Generate unique username and email for student

        Simple format: student_[random_string]
        This avoids issues with Korean character slugification.

        Args:
            name: Student name (not used in username, but kept for compatibility)
            school_name: School name (not used in username, but kept for compatibility)
            class_name: Class name (not used in username, but kept for compatibility)

        Returns:
            tuple: (username, email)
        """
        import time

        # Generate simple username with timestamp and random suffix
        timestamp = str(int(time.time() * 1000))[-8:]  # Last 8 digits of timestamp
        random_suffix = secrets.token_hex(4)  # 8 characters

        username = f"student_{timestamp}_{random_suffix}"

        # Check if username exists and regenerate if needed (should be very rare)
        counter = 0
        while User.objects.filter(username=username).exists():
            counter += 1
            random_suffix = secrets.token_hex(4)
            username = f"student_{timestamp}_{random_suffix}_{counter}"
            if counter > 10:  # Safety limit
                break

        # Generate email from username
        email = f"{username}@neulbom.internal"

        # Ensure email is unique
        counter = 1
        while Student.objects.filter(generated_email=email).exists():
            email = f"{username}{counter}@neulbom.internal"
            counter += 1

        return username, email


def create_student_accounts(
    students_data: List[Dict],
    class_assignment: Class,
    instructor_user
) -> Tuple[List[Student], List[Dict]]:
    """
    Create student accounts from parsed CSV data

    This function performs atomic bulk creation of:
    1. User accounts with student role
    2. Student profiles linked to User accounts

    Args:
        students_data: List of dicts with student information
        class_assignment: Class to assign students to
        instructor_user: Instructor creating the students

    Returns:
        tuple: (list of created Student objects, list of creation results)

    Raises:
        StudentCreationError: If bulk creation fails
    """
    logger.info(
        f"Creating {len(students_data)} student accounts "
        f"for class {class_assignment} by {instructor_user.username}"
    )

    created_students = []
    creation_results = []
    start_time = time.time()

    try:
        with transaction.atomic():
            for student_data in students_data:
                name = student_data.get('student_name', student_data.get('name', ''))  # Support both column names
                class_number = student_data.get('class_number')
                grade = student_data.get('grade', '')
                notes = student_data.get('notes', '')

                # Generate unique username and email for student
                username, email = StudentAccountService.generate_student_username(
                    name,
                    class_assignment.school.name,
                    class_assignment.name
                )

                # Check if username already exists (should be unique due to email generation logic)
                if User.objects.filter(username=username).exists():
                    error_msg = f"사용자명 {username}는 이미 존재합니다."
                    logger.warning(error_msg)
                    creation_results.append({
                        'name': name,
                        'class_number': class_number,
                        'success': False,
                        'error': error_msg
                    })
                    continue

                # Generate password
                password = generate_password()

                # Create User account
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    role='student',
                    first_name=name,
                    is_active=True,
                    affiliated_school=class_assignment.school
                )

                # Parse grade (handle both int from pandas and string from old code)
                grade_int = None
                if grade:
                    try:
                        if isinstance(grade, (int, float)):
                            grade_int = int(grade)
                        elif isinstance(grade, str) and grade.strip():
                            grade_int = int(grade.strip())
                    except (ValueError, AttributeError):
                        logger.warning(f"Invalid grade value: {grade}")

                # Parse class_number
                class_number_int = None
                if class_number:
                    try:
                        if isinstance(class_number, (int, float)):
                            class_number_int = int(class_number)
                        elif isinstance(class_number, str) and class_number.strip():
                            class_number_int = int(class_number.strip())
                    except (ValueError, AttributeError):
                        logger.warning(f"Invalid class_number value: {class_number}")

                # Create Student profile
                student = Student.objects.create(
                    user=user,
                    name=name,
                    class_number=class_number_int,
                    grade=grade_int,
                    class_assignment=class_assignment,
                    generated_email=email,
                    notes=notes
                )

                created_students.append(student)
                creation_results.append({
                    'name': name,
                    'class_number': class_number_int,
                    'grade': grade_int,
                    'username': username,
                    'password': password,
                    'email': email,
                    'success': True,
                    'error': None
                })

                logger.info(f"Created student account: {name} ({email})")

    except Exception as e:
        logger.error(f"Error during bulk student creation: {e}")
        raise StudentCreationError(f"학생 계정 생성 중 오류가 발생했습니다: {e}")

    elapsed_time = time.time() - start_time
    logger.info(
        f"Student creation complete. "
        f"Created: {len(created_students)}, "
        f"Failed: {len([r for r in creation_results if not r['success']])}, "
        f"Time: {elapsed_time:.2f}s"
    )

    return created_students, creation_results


def create_students_from_csv_with_auto_school_class(
    students_data: List[Dict],
    instructor_user
) -> Tuple[List[Student], List[Dict]]:
    """
    Create students from CSV data with auto-creation of schools and classes.

    This function processes CSV data that includes school_name and class_name,
    automatically creating schools and classes if they don't exist.

    Args:
        students_data: List of dicts with columns: school_name, class_name, student_name, class_number (optional), grade (optional), notes (optional)
        instructor_user: Instructor creating the students

    Returns:
        tuple: (list of created Student objects, list of creation results)

    Raises:
        StudentCreationError: If bulk creation fails
    """
    logger.info(
        f"Creating {len(students_data)} students with auto-school/class creation "
        f"by {instructor_user.username}"
    )

    created_students = []
    creation_results = []
    start_time = time.time()

    # Group students by (school_name, class_name) to minimize lookups
    from collections import defaultdict
    students_by_class = defaultdict(list)

    for student_data in students_data:
        school_name = student_data.get('school_name', '').strip()
        class_name = student_data.get('class_name', '').strip()
        key = (school_name, class_name)
        students_by_class[key].append(student_data)

    try:
        with transaction.atomic():
            for (school_name, class_name), students in students_by_class.items():
                # Get or create school
                school, school_created = School.objects.get_or_create(
                    name=school_name,
                    defaults={}
                )
                if school_created:
                    logger.info(f"Created new school: {school_name}")

                # Get or create class
                # Use current year and spring semester as defaults
                current_year = datetime.now().year
                class_obj, class_created = Class.objects.get_or_create(
                    name=class_name,
                    school=school,
                    instructor=instructor_user,
                    academic_year=current_year,
                    defaults={
                        'semester': 'spring'
                    }
                )
                if class_created:
                    logger.info(f"Created new class: {class_name} in {school_name}")

                # Create students in this class
                for student_data in students:
                    name = student_data.get('student_name', student_data.get('name', ''))
                    class_number = student_data.get('class_number')
                    grade = student_data.get('grade')
                    notes = student_data.get('notes', '')
                    zep_space_url = student_data.get('zep_space_url', '')

                    try:
                        # Generate unique username and email
                        username, email = StudentAccountService.generate_student_username(
                            name,
                            school_name,
                            class_name
                        )

                        # Generate password
                        password = generate_password()

                        # Create User account
                        user = User.objects.create_user(
                            username=username,
                            password=password,
                            email=email,
                            role='student',
                            first_name=name,
                            is_active=True,
                            affiliated_school=school
                        )

                        # Create Student profile
                        student = Student.objects.create(
                            user=user,
                            name=name,
                            class_number=int(class_number) if class_number and not pd.isna(class_number) else None,
                            grade=int(grade) if grade and not pd.isna(grade) else None,
                            class_assignment=class_obj,
                            generated_email=email,
                            notes=notes,
                            zep_space_url=zep_space_url if zep_space_url else ''
                        )

                        created_students.append(student)
                        creation_results.append({
                            'name': name,
                            'school_name': school_name,
                            'class_name': class_name,
                            'class_number': int(class_number) if class_number and not pd.isna(class_number) else None,
                            'grade': int(grade) if grade and not pd.isna(grade) else None,
                            'username': username,
                            'password': password,
                            'email': email,
                            'success': True,
                            'error': None
                        })

                        logger.info(f"Created student: {name} in {class_name} ({school_name})")

                    except Exception as e:
                        error_msg = f"{name} 생성 실패: {str(e)}"
                        logger.error(error_msg)
                        creation_results.append({
                            'name': name,
                            'school_name': school_name,
                            'class_name': class_name,
                            'class_number': class_number,
                            'grade': grade,
                            'success': False,
                            'error': error_msg
                        })

    except Exception as e:
        logger.error(f"Error during bulk student creation: {e}")
        raise StudentCreationError(f"학생 계정 생성 중 오류가 발생했습니다: {e}")

    elapsed_time = time.time() - start_time
    logger.info(
        f"Student creation complete. "
        f"Created: {len(created_students)}, "
        f"Failed: {len([r for r in creation_results if not r['success']])}, "
        f"Time: {elapsed_time:.2f}s"
    )

    return created_students, creation_results


def get_student_credentials(creation_results: List[Dict]) -> List[Dict]:
    """
    Extract student credentials from creation results

    Args:
        creation_results: List of creation result dicts

    Returns:
        list: List of dicts with student credentials
    """
    credentials = []

    for result in creation_results:
        if result['success']:
            credentials.append({
                'name': result['name'],
                'school_name': result.get('school_name', ''),
                'class_name': result.get('class_name', ''),
                'class_number': result.get('class_number'),
                'grade': result.get('grade'),
                'username': result['username'],
                'password': result['password'],
                'email': result['email']
            })

    return credentials


def export_credentials_csv(credentials: List[Dict]) -> str:
    """
    Generate CSV content with student credentials

    Args:
        credentials: List of credential dicts

    Returns:
        str: CSV content
    """
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['학교', '학급', '이름', '반번호', '학년', '아이디', '비밀번호'])

    # Write data
    for cred in credentials:
        writer.writerow([
            cred.get('school_name', '-'),
            cred.get('class_name', '-'),
            cred['name'],
            cred.get('class_number', '-'),
            cred.get('grade', '-'),
            cred['username'],
            cred['password']
        ])

    return output.getvalue()
