from django.contrib import admin
from core.models import ActivityLog, Album, Comment, Event, Guest, Invitation, Notification, Photo, SharedAlbum, UserProfile, InvitationCode

# Customize the admin site titles and headers
admin.site.site_header = "Shiv & Shakti App Administration"
admin.site.site_title = "Shiv & Shakti Admin Portal"
admin.site.index_title = "Welcome to Shiv & Shakti Admin Portal"

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0

class GuestInline(admin.TabularInline):
    model = Guest
    extra = 0

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class SharedAlbumInline(admin.TabularInline):
    model = SharedAlbum
    extra = 0

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'timestamp']
    search_fields = ['user__username', 'action']
    list_filter = ['user', 'timestamp']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    search_fields = ['name', 'user__username']
    list_filter = ['user', 'created_at']
    ordering = ['-created_at']
    inlines = [PhotoInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['photo', 'user', 'created_at']
    search_fields = ['photo__album__name', 'user__username']
    list_filter = ['user', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'date', 'created_at']
    search_fields = ['name', 'user__username']
    list_filter = ['user', 'date']
    ordering = ['-date']
    inlines = [GuestInline]

@admin.register(InvitationCode)
class InvitationCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'created_at']
    search_fields = ['user', 'code', 'created_at']
    list_filter = ['code', 'user', 'created_at']
    ordering = ['user']
    
@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'event']
    search_fields = ['name', 'email', 'event__name']
    list_filter = ['event']
    ordering = ['name']

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient_email', 'event', 'status', 'sent_at']
    search_fields = ['sender__username', 'recipient_email', 'event__name', 'status']
    list_filter = ['status', 'event', 'sent_at']
    ordering = ['-sent_at']
    readonly_fields = ['sent_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'created_at', 'read']
    search_fields = ['user__username', 'message']
    list_filter = ['user', 'created_at', 'read']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['album', 'caption', 'created_at']
    search_fields = ['album__name', 'caption']
    list_filter = ['album', 'created_at']
    ordering = ['-created_at']
    inlines = [CommentInline]

@admin.register(SharedAlbum)
class SharedAlbumAdmin(admin.ModelAdmin):
    list_display = ['album', 'shared_with', 'role', 'shared_at']
    search_fields = ['album__name', 'shared_with__username', 'role']
    list_filter = ['album', 'role', 'shared_at']
    ordering = ['-shared_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'event']
    search_fields = ['user__username', 'phone', 'event']
    list_filter = ['event']
    ordering = ['user__username']
