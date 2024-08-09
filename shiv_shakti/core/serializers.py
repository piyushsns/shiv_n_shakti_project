import django.template.loader
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (ActivityLog, Album, Comment, Event, Guest, Invitation, InvitationCode,
    Notification, Photo, SharedAlbum, UserProfile)
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class SharedAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedAlbum
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    event_type = serializers.CharField(write_only=True)
    event_date = serializers.DateField(write_only=True)
    selected_contacts = serializers.ListField(child=serializers.CharField(), write_only=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'confirm_password', 'event_type', 'event_date', 'selected_contacts']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        selected_contacts = validated_data.pop('selected_contacts', [])
        event_type = validated_data.pop('event_type')
        event_date = validated_data.pop('event_date')
        
        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Generate an invitation code for the user
        invitation_code = get_random_string(20)  # You can adjust the length
        InvitationCode.objects.create(user=user, code=invitation_code)
        
        # Create the event
        event = Event.objects.create(user=user, event_type=event_type, event_date=event_date)
        
        # Create user and invitation for each selected contact
        for contact_email in selected_contacts:
            contact_user, created = User.objects.get_or_create(
                username=contact_email.split('@')[0],  # Simplistic username generation
                email=contact_email,
                defaults={'is_active': False}  # Make sure the user is inactive initially
            )
            contact_invitation_code = get_random_string(20)
            InvitationCode.objects.create(user=contact_user, code=contact_invitation_code)
            Invitation.objects.create(
                sender=user,
                recipient_email=contact_email,
                event=event.event_type,
                invitation_code=invitation_code
            )
            self.send_invitation_email(user, contact_email, invitation_code)
        return user
    
    def send_invitation_email(self, user, contact_email, invitation_code):
        subject = f"You are invited to {user.first_name}'s event!"
        reset_url = f'{settings.FRONTEND_URL}/api/accept-invitation/{invitation_code}/'
        message = render_to_string('core/invitation_email.html', {
            'user': user,
            'reset_url': reset_url,
            'invitation_code': invitation_code,
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [contact_email],
            fail_silently=False,
            html_message=message
        )