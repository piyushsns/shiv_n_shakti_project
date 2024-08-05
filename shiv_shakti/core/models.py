from django.db import models
from django.contrib.auth.models import User
import face_recognition
from django.core.cache import cache
from PIL import Image
from PIL.ExifTags import TAGS

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    event = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Album(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    tagged_users = models.ManyToManyField(User, related_name='tagged_photos', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    date_taken = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.album.name} - {self.id}'

    def detect_faces(self):
        cached_faces = cache.get(f'faces_{self.id}')
        if cached_faces:
            return cached_faces
        image = face_recognition.load_image_file(self.image)
        face_locations = face_recognition.face_locations(image)
        cache.set(f'faces_{self.id}', face_locations, timeout=60*60*24)  # Cache for 24 hours
        return face_locations
    def extract_metadata(self):
        image = Image.open(self.image)
        info = image._getexif()
        if info:
            metadata = {TAGS.get(tag, tag): value for tag, value in info.items()}
            return metadata
        return {}

class Event(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    date = models.DateTimeField()
    albums = models.ManyToManyField(Album, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Guest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='guests')

    def __str__(self):
        return self.name

class Invitation(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    recipient_email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='invitations')
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Invitation from {self.sender} to {self.recipient_email}'

class Comment(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.photo.id}'

class SharedAlbum(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='shared_albums')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_albums')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.album.name} shared with {self.shared_with.username} as {self.role}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username} - {self.message}'

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)
    related_object = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'ActivityLog by {self.user.username} - {self.action}'