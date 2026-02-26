"""
Accounts Models - User management, authentication, and team functionality
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.validators import URLValidator


class UserProfile(models.Model):
    """Extended user profile with portfolio and collaboration data."""
    
    ROLE_CHOICES = [
        ('creator', 'Content Creator'),
        ('agency', 'Creative Agency'),
        ('educator', 'Educator'),
        ('student', 'Student'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, max_length=500, help_text="User biography or short description")
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True, help_text="Profile picture")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='creator')
    website = models.URLField(blank=True, null=True, help_text="Personal or business website")
    location = models.CharField(max_length=100, blank=True, null=True, help_text="User location")
    
    # Portfolio Display Settings
    is_public_portfolio = models.BooleanField(default=True, help_text="Make portfolio visible to public")
    portfolio_theme = models.CharField(
        max_length=50,
        default='light',
        choices=[('light', 'Light'), ('dark', 'Dark'), ('minimal', 'Minimal')],
        help_text="Theme for public portfolio"
    )
    
    # Statistics
    total_projects = models.IntegerField(default=0, help_text="Total number of created projects")
    total_views = models.IntegerField(default=0, help_text="Total portfolio views")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        indexes = [
            models.Index(fields=['user', 'is_public_portfolio']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} Profile"
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.user.username})
    
    def get_public_projects_count(self):
        """Return count of public projects."""
        return self.user.created_projects.filter(is_public=True).count()


class Team(models.Model):
    """Team model for collaborative project work."""
    
    name = models.CharField(max_length=200, unique=True, help_text="Team name")
    description = models.TextField(blank=True, null=True, max_length=500, help_text="Team description")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams', help_text="Team owner")
    logo = models.ImageField(upload_to='team_logos/%Y/%m/', blank=True, null=True, help_text="Team logo")
    
    # Membership
    members = models.ManyToManyField(User, through='TeamMembership', related_name='teams')
    
    # Settings
    is_public = models.BooleanField(default=False, help_text="Allow public discovery of team")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        indexes = [
            models.Index(fields=['owner', 'is_public']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('accounts:team_detail', kwargs={'pk': self.pk})
    
    def get_member_count(self):
        """Return total number of team members."""
        return self.members.count()
    
    def is_member(self, user):
        """Check if user is a team member."""
        return self.members.filter(pk=user.pk).exists()


class TeamMembership(models.Model):
    """Membership model with roles and permissions."""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
        ('commenter', 'Commenter'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('team', 'user')
        verbose_name = "Team Membership"
        verbose_name_plural = "Team Memberships"
    
    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"
    
    def can_edit(self):
        """Check if member can edit team projects."""
        return self.role in ['owner', 'editor']
    
    def can_view(self):
        """Check if member can view team projects."""
        return self.role in ['owner', 'editor', 'viewer', 'commenter']
    
    def can_comment(self):
        """Check if member can comment on projects."""
        return self.role in ['owner', 'editor', 'commenter']
