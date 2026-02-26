"""
Projects URL Configuration
"""
from django.urls import path
from projects import views

app_name = 'projects'

urlpatterns = [
    # Dashboard and main views
    path('', views.dashboard, name='dashboard'),
    path('create/', views.project_create, name='create'),
    path('browse/', views.browse_projects, name='browse'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    
    # Project views
    path('project/<slug:slug>/', views.project_detail, name='detail'),
    path('project/<slug:slug>/edit/', views.project_edit, name='edit'),
    path('project/<slug:slug>/publish/', views.project_publish, name='publish'),
    path('project/<slug:slug>/delete/', views.project_delete, name='delete'),
    
    # Interactions
    path('project/<slug:slug>/comment/', views.project_comment, name='comment'),
    path('project/<slug:slug>/like/', views.project_like, name='like'),
]
