"""
CSV export functionality for dashboard metrics.
"""

import csv
from django.http import HttpResponse
from datetime import datetime
from django.utils import timezone
import pytz


def to_kst(dt):
    """Convert datetime to KST (Korea Standard Time)."""
    if dt is None:
        return None
    kst = pytz.timezone('Asia/Seoul')
    if timezone.is_aware(dt):
        return dt.astimezone(kst)
    return kst.localize(dt)


def export_metrics_csv(metrics):
    """
    Export dashboard metrics to CSV with UTF-8 BOM for Excel compatibility.

    Args:
        metrics (dict): Dictionary containing dashboard metrics

    Returns:
        HttpResponse: CSV file response with proper encoding
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="dashboard_metrics_{timestamp}.csv"'

    # UTF-8 BOM for Excel compatibility
    response.write('\ufeff')

    writer = csv.writer(response)

    # Header
    writer.writerow(['Dashboard Metrics Export'])
    writer.writerow(['Export Time', metrics.get('timestamp', 'N/A')])
    writer.writerow([])  # Empty row

    # Core Metrics Section
    writer.writerow(['Core Metrics'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Schools', metrics.get('total_schools', 0)])
    writer.writerow(['Total Instructors', metrics.get('total_instructors', 0)])
    writer.writerow(['Total Students', metrics.get('total_students', 0)])
    writer.writerow(['Active Spaces', metrics.get('active_spaces', 0)])
    writer.writerow([])  # Empty row

    # Visitor Analytics Section
    visitor_stats = metrics.get('visitor_stats', {})
    writer.writerow(['Visitor Analytics'])
    writer.writerow(['Period', 'Count'])
    writer.writerow(['Daily (24h)', visitor_stats.get('daily', 0)])
    writer.writerow(['Weekly (7d)', visitor_stats.get('weekly', 0)])
    writer.writerow(['Monthly (30d)', visitor_stats.get('monthly', 0)])

    return response


def export_students_csv(students):
    """
    Export student list to CSV with UTF-8 BOM for Excel compatibility.

    Args:
        students (QuerySet): Student queryset to export

    Returns:
        HttpResponse: CSV file response with proper encoding
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="students_{timestamp}.csv"'

    # UTF-8 BOM for Excel compatibility (utf-8-sig already adds it)
    writer = csv.writer(response)

    # Header - clarify that email is system-generated login account
    writer.writerow([
        '이름',
        '반번호',
        '학년',
        '학급',
        '학교',
        '계정 이메일 (로그인용)',
        'ZEP 스페이스 URL',
        '스페이스 상태',
        '마지막 로그인 (KST)',
        '등록일 (KST)'
    ])

    # Data rows
    for student in students:
        # Get last login from user account
        last_login = None
        if student.user:
            last_login = student.user.last_login

        # Convert times to KST
        last_login_kst = to_kst(last_login) if last_login else None
        created_at_kst = to_kst(student.created_at) if student.created_at else None

        writer.writerow([
            student.name,
            student.class_number if student.class_number else '-',
            student.grade if student.grade else '-',
            student.class_assignment.name if student.class_assignment else 'N/A',
            student.class_assignment.school.name if student.class_assignment and student.class_assignment.school else 'N/A',
            student.generated_email,
            student.zep_space_url or '미생성',
            '생성됨' if student.is_space_created else '미생성',
            last_login_kst.strftime('%Y-%m-%d %H:%M:%S') if last_login_kst else '로그인 기록 없음',
            created_at_kst.strftime('%Y-%m-%d %H:%M:%S') if created_at_kst else 'N/A'
        ])

    return response
