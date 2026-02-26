"""
Accounts Admin Configuration
"""
from django.contrib import admin
from accounts.models import UserProfile, Team, TeamMembership


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_public_portfolio', 'total_projects', 'created_at')
    list_filter = ('role', 'is_public_portfolio', 'portfolio_theme', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')
    readonly_fields = ('total_projects', 'total_views', 'created_at', 'updated_at')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'role', 'joined_at')
    list_filter = ('role', 'team', 'joined_at')
    search_fields = ('user__username', 'team__name')
