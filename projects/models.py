"""
Projects Models - Project management, collections, and metadata
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class ProjectCategory(models.Model):
    """Categories for organizing projects."""
    
    name = models.CharField(max_length=100, unique=True, help_text="Category name")
    slug = models.SlugField(unique=True, help_text="URL-friendly slug")
    description = models.TextField(blank=True, null=True, max_length=500)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    
    class Meta:
        verbose_name = "Project Category"
        verbose_name_plural = "Project Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('projects:category', kwargs={'slug': self.slug})


class Project(models.Model):
    """Main project model containing multimedia content."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=255, help_text="Project title")
    slug = models.SlugField(unique=True, help_text="URL-friendly slug")
    description = models.TextField(blank=True, null=True, help_text="Project description")
    thumbnail = models.ImageField(upload_to='project_thumbnails/%Y/%m/', blank=True, null=True)
    
    # Creator Information
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    team = models.ForeignKey('accounts.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    
    # Categorization
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Settings
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=False, help_text="Make project visible to public")
    is_featured = models.BooleanField(default=False, help_text="Feature on portfolio")
    
    # Metadata
    view_count = models.IntegerField(default=0, help_text="Number of times project viewed")
    like_count = models.IntegerField(default=0, help_text="Number of likes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['creator', 'status']),
            models.Index(fields=['is_public', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'slug': self.slug})
    
    def publish(self):
        """Publish the project."""
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()
    
    def get_tags_list(self):
        """Return tags as a list."""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_media_count(self):
        """Return count of media files in project."""
        return self.media_files.count()
    
    def get_public_media(self):
        """Return publicly accessible media files."""
        return self.media_files.filter(is_public=True)
    
    def increment_view_count(self):
        """Increment view counter."""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def can_edit(self, user):
        """Check if user can edit this project."""
        if not user.is_authenticated:
            return False
        if self.creator == user:
            return True
        if self.team:
            membership = self.team.members.through.objects.filter(user=user, team=self.team).first()
            if membership and membership.can_edit():
                return True
        return False
    
    def can_view(self, user):
        """Check if user can view this project."""
        if self.is_public:
            return True
        if not user.is_authenticated:
            return False
        if self.creator == user:
            return True
        if self.team and self.team.is_member(user):
            return True
        return False


class ProjectCollection(models.Model):
    """Collections for organizing related projects."""
    
    name = models.CharField(max_length=255, help_text="Collection name")
    slug = models.SlugField(unique=True, help_text="URL-friendly slug")
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    projects = models.ManyToManyField(Project, related_name='collections', blank=True)
    
    is_public = models.BooleanField(default=False)
    order = models.IntegerField(default=0, help_text="Display order")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Project Collection"
        verbose_name_plural = "Project Collections"
        ordering = ['order', 'name']
        unique_together = ('owner', 'slug')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('projects:collection', kwargs={'owner': self.owner.username, 'slug': self.slug})


class ProjectComment(models.Model):
    """Comments on projects for collaboration and feedback."""
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_comments')
    
    content = models.TextField(help_text="Comment content")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Project Comment"
        verbose_name_plural = "Project Comments"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.project.title}"
    
    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'slug': self.project.slug})


class ProjectLike(models.Model):
    """Track project likes/favorites."""
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('project', 'user')
        verbose_name = "Project Like"
        verbose_name_plural = "Project Likes"
        indexes = [
            models.Index(fields=['project', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes {self.project.title}"
