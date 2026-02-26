"""
Media Models - File management and multimedia content handling
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import FileExtensionValidator
import os


class MediaAsset(models.Model):
    """Base model for all media assets uploaded to the platform."""
    
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=255, help_text="Media title")
    description = models.TextField(blank=True, null=True, max_length=500)
    
    # File Information
    file = models.FileField(
        upload_to='media/%Y/%m/%d/',
        help_text="Media file"
    )
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, help_text="Type of media")
    file_size = models.BigIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, blank=True, help_text="MIME type")
    
    # Owner Information
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_assets')
    
    # Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready')
    
    # Metadata
    is_public = models.BooleanField(default=False, help_text="Make media publicly accessible")
    duration = models.IntegerField(null=True, blank=True, help_text="Duration in seconds (for audio/video)")
    width = models.IntegerField(null=True, blank=True, help_text="Width in pixels (for images/video)")
    height = models.IntegerField(null=True, blank=True, help_text="Height in pixels (for images/video)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Media Asset"
        verbose_name_plural = "Media Assets"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'file_type']),
            models.Index(fields=['is_public', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('media:asset_detail', kwargs={'pk': self.pk})
    
    def get_file_extension(self):
        """Get file extension."""
        return os.path.splitext(self.file.name)[1].lower().lstrip('.')
    
    def get_display_filename(self):
        """Get original filename without path."""
        return os.path.basename(self.file.name)
    
    def mark_ready(self):
        """Mark media as ready for use."""
        self.status = 'ready'
        self.save(update_fields=['status'])


class ImageMedia(MediaAsset):
    """Specialized model for image files."""
    
    # Image-specific fields
    format = models.CharField(max_length=20, blank=True, help_text="Image format (JPEG, PNG, etc.)")
    is_thumbnail = models.BooleanField(default=False, help_text="Is this a thumbnail image")
    alt_text = models.CharField(max_length=255, blank=True, help_text="Alternative text for accessibility")
    
    class Meta:
        verbose_name = "Image Media"
        verbose_name_plural = "Image Media"
    
    def save(self, *args, **kwargs):
        """Auto-set file type."""
        if not self.file_type:
            self.file_type = 'image'
        super().save(*args, **kwargs)


class VideoMedia(MediaAsset):
    """Specialized model for video files."""
    
    QUALITY_CHOICES = [
        ('360p', '360p'),
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
        ('4k', '4K'),
    ]
    
    # Video-specific fields
    codec = models.CharField(max_length=50, blank=True, help_text="Video codec")
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='720p')
    thumbnail = models.ImageField(upload_to='video_thumbnails/%Y/%m/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Video Media"
        verbose_name_plural = "Video Media"
    
    def save(self, *args, **kwargs):
        """Auto-set file type."""
        if not self.file_type:
            self.file_type = 'video'
        super().save(*args, **kwargs)


class AudioMedia(MediaAsset):
    """Specialized model for audio files."""
    
    # Audio-specific fields
    artist = models.CharField(max_length=255, blank=True, help_text="Artist or creator name")
    album = models.CharField(max_length=255, blank=True, help_text="Album name")
    genre = models.CharField(max_length=100, blank=True, help_text="Music genre")
    codec = models.CharField(max_length=50, blank=True, help_text="Audio codec")
    bitrate = models.IntegerField(blank=True, null=True, help_text="Bitrate in kbps")
    
    class Meta:
        verbose_name = "Audio Media"
        verbose_name_plural = "Audio Media"
    
    def save(self, *args, **kwargs):
        """Auto-set file type."""
        if not self.file_type:
            self.file_type = 'audio'
        super().save(*args, **kwargs)


class DocumentMedia(MediaAsset):
    """Specialized model for document files."""
    
    DOCUMENT_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('doc', 'Word Document'),
        ('spreadsheet', 'Spreadsheet'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ]
    
    # Document-specific fields
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, default='pdf')
    page_count = models.IntegerField(blank=True, null=True, help_text="Number of pages")
    
    class Meta:
        verbose_name = "Document Media"
        verbose_name_plural = "Document Media"
    
    def save(self, *args, **kwargs):
        """Auto-set file type."""
        if not self.file_type:
            self.file_type = 'document'
        super().save(*args, **kwargs)


class ProjectMediaAssociation(models.Model):
    """Many-to-many relationship between projects and media with ordering."""
    
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='media_files')
    media = models.ForeignKey(MediaAsset, on_delete=models.CASCADE, related_name='used_in_projects')
    
    # Metadata
    order = models.IntegerField(default=0, help_text="Display order in project")
    caption = models.CharField(max_length=500, blank=True, help_text="Caption for this media in project")
    is_cover = models.BooleanField(default=False, help_text="Use as project cover image")
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('project', 'media')
        verbose_name = "Project Media Association"
        verbose_name_plural = "Project Media Associations"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.media.title} in {self.project.title}"


class MediaTag(models.Model):
    """Tags for organizing and searching media."""
    
    name = models.CharField(max_length=100, unique=True, help_text="Tag name")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    
    media_assets = models.ManyToManyField(MediaAsset, related_name='tags', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Media Tag"
        verbose_name_plural = "Media Tags"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('media:tag', kwargs={'slug': self.slug})
