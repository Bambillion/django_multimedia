"""
Projects Views - Project management, browsing, and collaboration
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import Http404

from projects.models import Project, ProjectCategory, ProjectCollection, ProjectComment, ProjectLike
from media.models import ProjectMediaAssociation


@login_required
def dashboard(request):
    """User dashboard showing projects and recent activity."""
    user = request.user
    projects = user.created_projects.all()
    recent_projects = projects.order_by('-created_at')[:6]
    
    context = {
        'projects': projects,
        'project_count': projects.count(),
        'recent_projects': recent_projects,
        'draft_count': projects.filter(status='draft').count(),
        'published_count': projects.filter(status='published').count(),
    }
    return render(request, 'projects/dashboard.html', context)


@login_required
def project_create(request):
    """Create a new project."""
    categories = ProjectCategory.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        tags = request.POST.get('tags', '')
        
        if not title:
            messages.error(request, 'Project title is required.')
            return redirect('projects:create')
        
        try:
            category = None
            if category_id:
                category = ProjectCategory.objects.get(id=category_id)
            
            project = Project.objects.create(
                title=title,
                description=description,
                category=category,
                tags=tags,
                creator=request.user,
                status='draft',
            )
            messages.success(request, 'Project created successfully.')
            return redirect('projects:edit', slug=project.slug)
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
            return redirect('projects:create')
    
    context = {'categories': categories}
    return render(request, 'projects/create.html', context)


@login_required
def project_edit(request, slug):
    """Edit project details."""
    project = get_object_or_404(Project, slug=slug)
    
    if not project.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('projects:detail', slug=slug)
    
    categories = ProjectCategory.objects.all()
    media_files = project.media_files.all().order_by('order')
    
    if request.method == 'POST':
        project.title = request.POST.get('title', project.title)
        project.description = request.POST.get('description', project.description)
        project.tags = request.POST.get('tags', project.tags)
        project.is_public = request.POST.get('is_public') == 'on'
        project.is_featured = request.POST.get('is_featured') == 'on'
        
        category_id = request.POST.get('category')
        if category_id:
            project.category = ProjectCategory.objects.get(id=category_id)
        
        if 'thumbnail' in request.FILES:
            project.thumbnail = request.FILES['thumbnail']
        
        try:
            project.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('projects:detail', slug=project.slug)
        except Exception as e:
            messages.error(request, f'Error updating project: {str(e)}')
    
    context = {
        'project': project,
        'categories': categories,
        'media_files': media_files,
    }
    return render(request, 'projects/edit.html', context)


def project_detail(request, slug):
    """View project details."""
    project = get_object_or_404(Project, slug=slug)
    
    # Check access
    if not project.can_view(request.user):
        raise Http404("Project not found.")
    
    # Increment view count
    project.increment_view_count()
    
    # Get media files
    media_files = project.media_files.all().order_by('order')
    
    # Get comments
    comments = project.comments.all().order_by('-created_at')
    
    # Check if user liked this project
    user_liked = False
    if request.user.is_authenticated:
        user_liked = project.likes.filter(user=request.user).exists()
    
    context = {
        'project': project,
        'media_files': media_files,
        'comments': comments,
        'comment_count': comments.count(),
        'user_liked': user_liked,
        'can_edit': project.can_edit(request.user),
    }
    return render(request, 'projects/detail.html', context)


@login_required
def project_publish(request, slug):
    """Publish a project."""
    project = get_object_or_404(Project, slug=slug)
    
    if not project.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('projects:detail', slug=slug)
    
    project.publish()
    messages.success(request, 'Project published successfully.')
    return redirect('projects:detail', slug=project.slug)


@login_required
def project_delete(request, slug):
    """Delete a project."""
    project = get_object_or_404(Project, slug=slug)
    
    if not project.can_edit(request.user):
        messages.error(request, 'You do not have permission to delete this project.')
        return redirect('projects:detail', slug=slug)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('projects:dashboard')
    
    context = {'project': project}
    return render(request, 'projects/confirm_delete.html', context)


def browse_projects(request):
    """Browse all public projects."""
    projects = Project.objects.filter(is_public=True, status='published')
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        projects = projects.filter(category__slug=category_slug)
    
    # Search
    search = request.GET.get('search')
    if search:
        projects = projects.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    projects = projects.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    categories = ProjectCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'projects': page_obj.object_list,
        'categories': categories,
        'search': search,
        'selected_category': category_slug,
    }
    return render(request, 'projects/browse.html', context)


@login_required
def project_comment(request, slug):
    """Add comment to project."""
    if request.method != 'POST':
        return redirect('projects:detail', slug=slug)
    
    project = get_object_or_404(Project, slug=slug)
    content = request.POST.get('content', '').strip()
    
    if not content:
        messages.error(request, 'Comment cannot be empty.')
        return redirect('projects:detail', slug=slug)
    
    try:
        ProjectComment.objects.create(
            project=project,
            author=request.user,
            content=content,
        )
        messages.success(request, 'Comment posted successfully.')
    except Exception as e:
        messages.error(request, f'Error posting comment: {str(e)}')
    
    return redirect('projects:detail', slug=slug)


@login_required
def project_like(request, slug):
    """Like or unlike a project."""
    project = get_object_or_404(Project, slug=slug)
    
    like_obj = project.likes.filter(user=request.user).first()
    
    if like_obj:
        like_obj.delete()
        project.like_count = max(0, project.like_count - 1)
        project.save(update_fields=['like_count'])
        messages.success(request, 'Like removed.')
    else:
        ProjectLike.objects.create(project=project, user=request.user)
        project.like_count += 1
        project.save(update_fields=['like_count'])
        messages.success(request, 'Project liked!')
    
    return redirect('projects:detail', slug=project.slug)


def category_view(request, slug):
    """View projects in a category."""
    category = get_object_or_404(ProjectCategory, slug=slug)
    projects = category.projects.filter(is_public=True, status='published').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'projects': page_obj.object_list,
    }
    return render(request, 'projects/category.html', context)
