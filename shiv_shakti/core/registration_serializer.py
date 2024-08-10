from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, InvitationCode, Album, Event, Invitation, Guest
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .utils import send_email_via_api
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
    
class RegistrationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    event_type = serializers.CharField(write_only=True)
    event_date = serializers.DateField(write_only=True)
    selected_contacts = serializers.ListField(child=serializers.JSONField(), write_only=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'username', 'password', 'event_type', 'event_date', 'selected_contacts']

    def create(self, validated_data):
        selected_contacts = validated_data.pop('selected_contacts', [])
        event_type = validated_data.pop('event_type')
        phone = validated_data.pop('phone')
        event_date = validated_data.pop('event_date')

        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        UserProfile.objects.create(
            user=user,
            phone=phone
        )
        
        # Generate an invitation code for the user
        invitation_code = get_random_string(20)  # Adjust the length as needed
        InvitationCode.objects.create(user=user, code=invitation_code)
        
        # Create the event and associate it with the user's albums
        event = Event.objects.create(user=user, name=event_type, date=event_date)
        Album.objects.create(user=user, name="All", description="All Photos")
        # Set albums for the event
        user_albums = Album.objects.filter(user=user)
        event.albums.set(user_albums)  # Use the set() method her
        # Create user and invitation for each selected contact
        for selected_contact in selected_contacts:
            contact_user, created = User.objects.get_or_create(
                username=selected_contact['email'].split('@')[0], 
                defaults={
                    'first_name': selected_contact['first_name'],
                    'last_name': selected_contact['last_name'],
                    'email': selected_contact['email'],
                    'is_active': False
                }
            )
            contact_invitation_code = get_random_string(20)
            InvitationCode.objects.create(user=contact_user, code=contact_invitation_code)
            
            # Create invitation for the event
            Invitation.objects.create(
                sender=user,
                recipient_email=selected_contact['email'],
                event=event,
                invitation_code=contact_invitation_code
            )
            
            # Create user profile for the contact user
            UserProfile.objects.create(
                user=contact_user,
                phone=selected_contact.get('phone', '')
            )
            
            # Create guest entry for the event
            Guest.objects.create(
                event=event,
                name=f"{selected_contact['first_name']} {selected_contact['last_name']}",
                email=selected_contact['email'],
                phone=selected_contact.get('phone', '')
            )
            
            # Create an album for the contact user
            Album.objects.create(user=contact_user, name="All", description="All Photos")
            
            # Send an invitation email to the contact user
            self.send_invitation_email(user, selected_contact['email'], contact_invitation_code)
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        return user
        return Response({
            'succesLoggged': True,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data,
        })
    
    def send_invitation_email(self, user, contact_email, invitation_code):
        subject = f"You are invited to {user.first_name}'s event!"
        reset_url = f'{settings.FRONTEND_URL}/api/accept-invitation/{invitation_code}/'
        message = render_to_string('core/invitation_email.html', {
            'user': user,
            'reset_url': reset_url,
            'invitation_code': invitation_code,
        })
        to_email = contact_email
        subject = "sns subject12"
        message = "This is for testing1"
        attachments = []
        send_email_via_api(to_email, subject, message, attachments)
        # Return the API response as a JSON response

