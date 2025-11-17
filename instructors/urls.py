from django.urls import path
from . import views

app_name = 'instructors'

urlpatterns = [
    path('', views.instructor_list, name='list'),
    path('create/', views.instructor_create, name='create'),
    path('<int:pk>/', views.instructor_detail, name='detail'),
    path('<int:pk>/edit/', views.instructor_edit, name='edit'),
    path('class/create/', views.class_create, name='class_create'),
]
