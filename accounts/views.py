"""
Accounts Views - User authentication, registration, and profile management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction

from accounts.models import UserProfile, Team, TeamMembership


@require_http_methods(["GET", "POST"])
def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('projects:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        full_name = request.POST.get('full_name', '')
        
        # Validation
        if not all([username, email, password, password_confirm]):
            messages.error(request, 'All fields are required.')
            return redirect('accounts:register')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('accounts:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('accounts:register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('accounts:register')
        
        # Create user and profile
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=full_name.split()[0] if full_name else '',
                    last_name=' '.join(full_name.split()[1:]) if full_name else '',
                )
                # UserProfile is created automatically by signal
                
            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('accounts:register')
    
    return render(request, 'accounts/register.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('projects:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return redirect('accounts:login')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('projects:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('accounts:login')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile_edit(request):
    """Edit user profile."""
    profile = request.user.profile
    
    if request.method == 'POST':
        profile.bio = request.POST.get('bio', '')
        profile.role = request.POST.get('role', profile.role)
        profile.website = request.POST.get('website', '')
        profile.location = request.POST.get('location', '')
        profile.is_public_portfolio = request.POST.get('is_public_portfolio') == 'on'
        profile.portfolio_theme = request.POST.get('portfolio_theme', profile.portfolio_theme)
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        # Update user fields
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', request.user.email)
        
        try:
            profile.save()
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile', username=request.user.username)
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'profile': profile,
        'role_choices': UserProfile.ROLE_CHOICES,
        'theme_choices': UserProfile._meta.get_field('portfolio_theme').choices,
    }
    return render(request, 'accounts/profile_edit.html', context)


def profile_view(request, username):
    """View user profile and portfolio."""
    user = get_object_or_404(User, username=username)
    profile = user.profile
    
    # Check if profile is public
    if not profile.is_public_portfolio and request.user != user:
        messages.error(request, 'This portfolio is private.')
        return redirect('projects:dashboard')
    
    # Get public projects
    projects = user.created_projects.filter(is_public=True, status='published')
    
    # Increment view count
    if request.user != user:
        profile.total_views += 1
        profile.save(update_fields=['total_views'])
    
    context = {
        'viewed_user': user,
        'profile': profile,
        'projects': projects,
        'project_count': projects.count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def team_list(request):
    """List user's teams."""
    teams = request.user.teams.all()
    owned_teams = request.user.owned_teams.all()
    
    context = {
        'teams': teams,
        'owned_teams': owned_teams,
    }
    return render(request, 'accounts/team_list.html', context)


@login_required
def team_create(request):
    """Create a new team."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'
        
        if not name:
            messages.error(request, 'Team name is required.')
            return redirect('accounts:team_create')
        
        try:
            team = Team.objects.create(
                name=name,
                description=description,
                owner=request.user,
                is_public=is_public,
            )
            TeamMembership.objects.create(
                team=team,
                user=request.user,
                role='owner',
            )
            messages.success(request, f'Team "{name}" created successfully.')
            return redirect('accounts:team_detail', pk=team.pk)
        except Exception as e:
            messages.error(request, f'Error creating team: {str(e)}')
            return redirect('accounts:team_create')
    
    return render(request, 'accounts/team_create.html')


def team_detail(request, pk):
    """View team details."""
    team = get_object_or_404(Team, pk=pk)
    
    # Check access
    if not team.is_public and not team.is_member(request.user):
        messages.error(request, 'You do not have access to this team.')
        return redirect('projects:dashboard')
    
    members = team.members.all()
    projects = team.projects.all()
    
    context = {
        'team': team,
        'members': members,
        'projects': projects,
        'is_owner': team.owner == request.user,
    }
    return render(request, 'accounts/team_detail.html', context)


@login_required
def team_add_member(request, pk):
    """Add member to team."""
    team = get_object_or_404(Team, pk=pk)
    
    # Check ownership
    if team.owner != request.user:
        messages.error(request, 'Only team owner can add members.')
        return redirect('accounts:team_detail', pk=pk)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        role = request.POST.get('role', 'viewer')
        
        try:
            user = get_object_or_404(User, username=username)
            
            if team.is_member(user):
                messages.warning(request, 'User is already a team member.')
                return redirect('accounts:team_detail', pk=pk)
            
            TeamMembership.objects.create(
                team=team,
                user=user,
                role=role,
            )
            messages.success(request, f'User "{username}" added to team.')
            return redirect('accounts:team_detail', pk=pk)
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'Error adding member: {str(e)}')
    
    return render(request, 'accounts/team_add_member.html', {'team': team})
