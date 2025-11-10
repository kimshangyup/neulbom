from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/export/', views.export_metrics, name='export_metrics'),
    path('admin/instructor/<int:instructor_id>/', views.instructor_detail, name='instructor_detail'),
    path('api/metrics/', views.metrics_api, name='metrics_api'),
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/export/', views.export_students, name='export_students'),
    path('instructor/api/schools/', views.get_schools, name='get_schools'),
    path('instructor/api/create-school/', views.create_school, name='create_school'),
    path('instructor/api/create-class/', views.create_class, name='create_class'),
    path('instructor/api/create-student/', views.create_student, name='create_student'),
    path('instructor/api/update-student/<int:student_id>/', views.update_student, name='update_student'),
]
