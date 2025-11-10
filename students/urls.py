from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('upload-csv/', views.student_upload, name='upload-csv'),
    path('<int:pk>/edit-space/', views.student_edit_space, name='edit_space'),
    path('credentials/', views.student_credentials, name='credentials'),
    path('download-credentials/', views.download_credentials, name='download_credentials'),
    path('csv-template/download/', views.download_template, name='download-template'),
]
