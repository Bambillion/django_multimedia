"""
Media Admin Configuration
"""
from django.contrib import admin
from media.models import MediaAsset, ImageMedia, VideoMedia, AudioMedia, DocumentMedia, ProjectMediaAssociation, MediaTag


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'file_type', 'status', 'is_public', 'created_at')
    list_filter = ('file_type', 'status', 'is_public', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    readonly_fields = ('file_size', 'mime_type', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(ImageMedia)
class ImageMediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'format', 'is_thumbnail', 'created_at')
    list_filter = ('is_thumbnail', 'created_at')
    search_fields = ('title', 'owner__username')


@admin.register(VideoMedia)
class VideoMediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'quality', 'duration', 'created_at')
    list_filter = ('quality', 'created_at')
    search_fields = ('title', 'owner__username')


@admin.register(AudioMedia)
class AudioMediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'duration', 'created_at')
    list_filter = ('genre', 'created_at')
    search_fields = ('title', 'artist', 'album', 'owner__username')


@admin.register(DocumentMedia)
class DocumentMediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'document_type', 'page_count', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('title', 'owner__username')


@admin.register(ProjectMediaAssociation)
class ProjectMediaAssociationAdmin(admin.ModelAdmin):
    list_display = ('project', 'media', 'order', 'is_cover', 'added_at')
    list_filter = ('is_cover', 'added_at')
    search_fields = ('project__title', 'media__title')


@admin.register(MediaTag)
class MediaTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
