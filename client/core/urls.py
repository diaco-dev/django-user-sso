from django.urls import path
from . import views

urlpatterns = [
    # API status
    path('status/', views.api_status, name='api_status'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Projects
    path('projects/', views.ProjectListCreateView.as_view(), name='project_list_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),

    # Tasks
    path('projects/<int:project_id>/tasks/', views.TaskListCreateView.as_view(), name='task_list_create'),
    path('projects/<int:project_id>/tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),

    # Comments
    path('projects/<int:project_id>/tasks/<int:task_id>/comments/', views.CommentListCreateView.as_view(),
         name='comment_list_create'),
]