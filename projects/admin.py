"""
Projects Admin Configuration
"""
from django.contrib import admin
from projects.models import ProjectCategory, Project, ProjectCollection, ProjectComment, ProjectLike


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'status', 'is_public', 'view_count', 'created_at')
    list_filter = ('status', 'is_public', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'description', 'creator__username', 'tags')
    readonly_fields = ('slug', 'view_count', 'like_count', 'created_at', 'updated_at', 'published_at')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'


@admin.register(ProjectCollection)
class ProjectCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'owner__username')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'author', 'created_at')
    list_filter = ('created_at', 'project')
    search_fields = ('content', 'author__username', 'project__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProjectLike)
class ProjectLikeAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'project__title')
