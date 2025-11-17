"""
Space management services

Business logic for ZEP space creation and permission management
"""

from django.conf import settings
from typing import List, Dict, Optional
import logging
from datetime import datetime

from students.models import Student, FailedSpaceCreation
from .zep_client import get_zep_client, ZEPAPIError

logger = logging.getLogger(__name__)


def create_student_space(
    student: Student,
    instructor_email: str,
    admin_emails: Optional[List[str]] = None
) -> Dict:
    """
    Create ZEP space for a student and configure permissions

    Args:
        student: Student object
        instructor_email: Instructor's email (will be added as staff)
        admin_emails: List of admin emails (will be added as staff)

    Returns:
        dict: Space creation result with success status and space info

    Raises:
        ZEPAPIError: If space creation or permission setting fails
    """
    logger.info(f"Creating ZEP space for student: {student.name} ({student.generated_email})")

    zep_client = get_zep_client()

    # Generate space name
    current_year = datetime.now().year
    space_name = f"{student.name}_portfolio_{current_year}"

    try:
        # Step 1: Create space
        space_result = zep_client.create_space(
            name=space_name,
            owner_email=student.generated_email,
            template_id=getattr(settings, 'ZEP_SPACE_TEMPLATE_ID', None),
            description=f"{student.name}의 포트폴리오 스페이스"
        )

        space_id = space_result.get('space_id')
        space_url = space_result.get('url')

        if not space_id or not space_url:
            raise ZEPAPIError("Space creation response missing space_id or url")

        logger.info(f"Space created: {space_id}")

        # Step 2: Set permissions
        staff_emails = [instructor_email]
        if admin_emails:
            staff_emails.extend(admin_emails)

        permission_result = zep_client.set_space_permissions(
            space_id=space_id,
            owner_email=student.generated_email,
            staff_emails=staff_emails
        )

        logger.info(f"Permissions configured for space: {space_id}")

        # Step 3: Update student record with space URL
        student.zep_space_url = space_url
        student.save()

        return {
            'success': True,
            'space_id': space_id,
            'space_url': space_url,
            'student': student,
            'error': None
        }

    except ZEPAPIError as e:
        error_msg = str(e)
        logger.error(f"Failed to create space for student {student.name} ({student.generated_email}): {error_msg}")

        # Record failure for manual review
        FailedSpaceCreation.objects.create(
            student=student,
            error_message=error_msg,
            retry_count=0
        )

        return {
            'success': False,
            'space_id': None,
            'space_url': None,
            'student': student,
            'error': error_msg
        }


def create_spaces_for_students(
    students: List[Student],
    instructor_email: str,
    admin_emails: Optional[List[str]] = None
) -> Dict:
    """
    Create ZEP spaces for multiple students

    Args:
        students: List of Student objects
        instructor_email: Instructor's email
        admin_emails: List of admin emails

    Returns:
        dict: Summary with success/failure counts and results
    """
    logger.info(f"Creating spaces for {len(students)} students")

    results = {
        'total': len(students),
        'success': 0,
        'failed': 0,
        'details': []
    }

    for student in students:
        result = create_student_space(
            student=student,
            instructor_email=instructor_email,
            admin_emails=admin_emails
        )

        results['details'].append(result)

        if result['success']:
            results['success'] += 1
        else:
            results['failed'] += 1

    logger.info(
        f"Space creation complete. "
        f"Success: {results['success']}, "
        f"Failed: {results['failed']}"
    )

    return results


def retry_failed_space_creation(failed_creation: FailedSpaceCreation) -> bool:
    """
    Retry creating space for a failed attempt

    Args:
        failed_creation: FailedSpaceCreation record

    Returns:
        bool: True if retry successful
    """
    logger.info(f"Retrying space creation for student: {failed_creation.student.name} ({failed_creation.student.generated_email})")

    student = failed_creation.student
    instructor_email = student.class_assignment.instructor.email if student.class_assignment else None

    if not instructor_email:
        logger.error("Cannot retry: instructor email not found")
        return False

    result = create_student_space(
        student=student,
        instructor_email=instructor_email
    )

    if result['success']:
        # Mark as resolved
        failed_creation.resolved = True
        failed_creation.resolved_at = datetime.now()
        failed_creation.save()
        logger.info(f"Space creation retry successful for student: {student.name} ({student.generated_email})")
        return True
    else:
        # Increment retry count
        failed_creation.retry_count += 1
        failed_creation.save()
        logger.warning(f"Space creation retry failed for student: {student.name} ({student.generated_email})")
        return False


def get_admin_emails() -> List[str]:
    """
    Get list of administrator emails for space permissions

    Returns:
        list: List of admin email addresses
    """
    from authentication.models import User

    admin_users = User.objects.filter(
        role='admin',
        is_active=True
    ).exclude(email='')

    return list(admin_users.values_list('email', flat=True))
