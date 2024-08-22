from django.urls import path
from . import views

urlpatterns = [
    # HTML form views
    path('', views.logout_view, name='logout'),
    path('logout/', views.logout_view, name='logout'),
    path('menu/', views.menu_list, name='menu_list'),
    path('register/', views.user_register_view, name='user_register'),
    path('login/', views.user_login_view, name='user_login'),
    path('tasks/', views.create_task_view, name='create_task'),  # Changed to avoid conflict
    path('tasks/list/', views.task_view_list, name='task_list'),       # Changed to avoid conflict
    path('tasks/manage-members/', views.manage_members_view, name='manage_members'),

    # API endpoints
    path('api/register/', views.user_register, name='api_user_register'),
    path('api/login/', views.user_login, name='api_user_login'),        # Adjusted to align with convention
    path('api/tasks/create/', views.create_task, name='api_create_task'),
    path('api/tasks/', views.task_list, name='api_tasks_list'),        # Adjusted to include trailing slash
    path('api/tasks/<int:pk>/', views.task_detail, name='api_task_detail'),
    path('api/tasks/<int:pk>/update/', views.update_task, name='api_update_task'),
    path('api/tasks/<int:pk>/delete/', views.delete_task, name='api_delete_task'),
    path('api/tasks/<int:pk>/members/add/', views.add_task_member, name='api_add_task_member'),
    path('api/tasks/<int:pk>/members/remove/', views.remove_task_member, name='api_remove_task_member'),
    path('api/tasks/<int:pk>/members/', views.view_task_members, name='api_view_task_members'),
    path('api/tasks/<int:pk>/status/', views.update_task_status, name='api_update_task_status'),
    
    
]
