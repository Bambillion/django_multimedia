"""
Media Views - Media upload, management, and serving
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.conf import settings
import mimetypes
import os

from media.models import MediaAsset, ImageMedia, VideoMedia, AudioMedia, DocumentMedia, ProjectMediaAssociation
from projects.models import Project


@login_required
def media_library(request):
    """View user's media library."""
    media_assets = request.user.media_assets.all().order_by('-created_at')
    
    # Filter by type
    file_type = request.GET.get('type')
    if file_type:
        media_assets = media_assets.filter(file_type=file_type)
    
    # Search
    search = request.GET.get('search')
    if search:
        media_assets = media_assets.filter(title__icontains=search)
    
    context = {
        'media_assets': media_assets,
        'total_count': request.user.media_assets.count(),
        'image_count': request.user.media_assets.filter(file_type='image').count(),
        'video_count': request.user.media_assets.filter(file_type='video').count(),
        'audio_count': request.user.media_assets.filter(file_type='audio').count(),
        'document_count': request.user.media_assets.filter(file_type='document').count(),
    }
    return render(request, 'media/library.html', context)


@login_required
@require_http_methods(["POST"])
def media_upload(request):
    """Upload media file."""
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    uploaded_file = request.FILES['file']
    title = request.POST.get('title', uploaded_file.name)
    description = request.POST.get('description', '')
    is_public = request.POST.get('is_public') == 'true'
    
    # Validate file size
    if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
        return JsonResponse(
            {'error': f'File size exceeds limit of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB'},
            status=400
        )
    
    # Get file type
    mime_type, _ = mimetypes.guess_type(uploaded_file.name)
    file_extension = os.path.splitext(uploaded_file.name)[1].lower().lstrip('.')
    
    # Determine file type
    file_type = 'other'
    if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
        file_type = 'image'
    elif file_extension in ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv']:
        file_type = 'video'
    elif file_extension in ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg']:
        file_type = 'audio'
    elif file_extension in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
        file_type = 'document'
    
    # Validate file type
    if file_extension not in settings.ALLOWED_FILE_TYPES:
        return JsonResponse(
            {'error': f'File type .{file_extension} is not allowed'},
            status=400
        )
    
    try:
        media = MediaAsset.objects.create(
            title=title,
            description=description,
            file=uploaded_file,
            file_type=file_type,
            file_size=uploaded_file.size,
            mime_type=mime_type,
            owner=request.user,
            is_public=is_public,
        )
        
        return JsonResponse({
            'success': True,
            'media_id': media.id,
            'title': media.title,
            'file_type': media.file_type,
            'url': media.get_absolute_url(),
        })
    except Exception as e:
        return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)


@login_required
def media_detail(request, pk):
    """View media details."""
    media = get_object_or_404(MediaAsset, pk=pk)
    
    # Check access
    if not media.is_public and media.owner != request.user:
        raise Http404("Media not found.")
    
    # Get projects using this media
    projects = media.used_in_projects.all()
    
    context = {
        'media': media,
        'projects': projects,
        'can_edit': media.owner == request.user,
    }
    return render(request, 'media/detail.html', context)


@login_required
def media_edit(request, pk):
    """Edit media metadata."""
    media = get_object_or_404(MediaAsset, pk=pk)
    
    if media.owner != request.user:
        messages.error(request, 'You do not have permission to edit this media.')
        return redirect('media:library')
    
    if request.method == 'POST':
        media.title = request.POST.get('title', media.title)
        media.description = request.POST.get('description', media.description)
        media.is_public = request.POST.get('is_public') == 'on'
        
        try:
            media.save()
            messages.success(request, 'Media updated successfully.')
            return redirect('media:detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Error updating media: {str(e)}')
    
    context = {'media': media}
    return render(request, 'media/edit.html', context)


@login_required
def media_delete(request, pk):
    """Delete media."""
    media = get_object_or_404(MediaAsset, pk=pk)
    
    if media.owner != request.user:
        messages.error(request, 'You do not have permission to delete this media.')
        return redirect('media:library')
    
    if request.method == 'POST':
        # Delete associated file
        if media.file:
            media.file.delete()
        media.delete()
        messages.success(request, 'Media deleted successfully.')
        return redirect('media:library')
    
    context = {'media': media}
    return render(request, 'media/confirm_delete.html', context)


@login_required
def add_media_to_project(request, slug):
    """Add media to a project."""
    project = get_object_or_404(Project, slug=slug)
    
    if not project.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('projects:detail', slug=slug)
    
    if request.method == 'POST':
        media_id = request.POST.get('media_id')
        caption = request.POST.get('caption', '')
        is_cover = request.POST.get('is_cover') == 'on'
        
        try:
            media = MediaAsset.objects.get(id=media_id, owner=request.user)
            
            # Get next order
            next_order = project.media_files.count()
            
            association = ProjectMediaAssociation.objects.create(
                project=project,
                media=media,
                caption=caption,
                is_cover=is_cover,
                order=next_order,
            )
            
            messages.success(request, 'Media added to project.')
            return redirect('projects:edit', slug=slug)
        except MediaAsset.DoesNotExist:
            messages.error(request, 'Media not found.')
        except Exception as e:
            messages.error(request, f'Error adding media: {str(e)}')
    
    user_media = request.user.media_assets.all().order_by('-created_at')
    context = {
        'project': project,
        'user_media': user_media,
    }
    return render(request, 'media/add_to_project.html', context)


@login_required
def remove_media_from_project(request, pk):
    """Remove media from project."""
    association = get_object_or_404(ProjectMediaAssociation, pk=pk)
    
    if not association.project.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('projects:detail', slug=association.project.slug)
    
    project_slug = association.project.slug
    association.delete()
    messages.success(request, 'Media removed from project.')
    return redirect('projects:edit', slug=project_slug)
