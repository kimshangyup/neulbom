"""
CSV export functionality for dashboard metrics.
"""

import csv
from django.http import HttpResponse
from datetime import datetime


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

    # Header
    writer.writerow(['Name', 'Class Number', 'Grade', 'Class', 'School', 'Email', 'ZEP Space URL', 'Space Status', 'Last Activity'])

    # Data rows
    for student in students:
        writer.writerow([
            student.name,
            student.class_number if student.class_number else '-',
            student.grade if student.grade else '-',
            student.class_assignment.name if student.class_assignment else 'N/A',
            student.class_assignment.school.name if student.class_assignment and student.class_assignment.school else 'N/A',
            student.generated_email,
            student.zep_space_url or 'Not Created',
            'Created' if student.is_space_created else 'Not Created',
            student.updated_at.strftime('%Y-%m-%d %H:%M:%S') if student.updated_at else 'N/A'
        ])

    return response
