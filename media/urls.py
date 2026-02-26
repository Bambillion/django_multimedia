"""
Media URL Configuration
"""
from django.urls import path
from media import views

app_name = 'media'

urlpatterns = [
    # Library and browsing
    path('library/', views.media_library, name='library'),
    path('upload/', views.media_upload, name='upload'),
    
    # Media management
    path('media/<int:pk>/', views.media_detail, name='detail'),
    path('media/<int:pk>/edit/', views.media_edit, name='edit'),
    path('media/<int:pk>/delete/', views.media_delete, name='delete'),
    
    # Project association
    path('project/<slug:slug>/add-media/', views.add_media_to_project, name='add_to_project'),
    path('association/<int:pk>/remove/', views.remove_media_from_project, name='remove_from_project'),
]
