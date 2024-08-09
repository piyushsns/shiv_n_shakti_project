from rest_framework import viewsets, filters, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.utils import send_email_via_api
from .models import UserProfile, Album, Photo, Event, Guest, Invitation, Comment, SharedAlbum, Notification, ActivityLog
from .serializers import *
from .registration_serializer import RegistrationSerializer
from haystack.query import SearchQuerySet
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import render, get_object_or_404
from .forms import AcceptInvitationForm
from django.contrib import messages
from django_filters.rest_framework import DjangoFilterBackend
from .utils import upload_file_to_s3
from django.utils.http import urlsafe_base64_decode
from rest_framework import status

class SearchView(generics.ListAPIView):
    serializer_class = serializers.SerializerMethodField()
    def get_serializer_class(self):
        model = self.request.query_params.get('model')
        if model == 'album':
            return AlbumSerializer
        elif model == 'photo':
            return PhotoSerializer
        elif model == 'event':
            return EventSerializer

    def get_queryset(self):
        model = self.request.query_params.get('model')
        query = self.request.query_params.get('q')
        if model == 'album':
            return SearchQuerySet().models(Album).filter(content=query)
        elif model == 'photo':
            return SearchQuerySet().models(Photo).filter(content=query)
        elif model == 'event':
            return SearchQuerySet().models(Event).filter(content=query)
        
class RegistrationUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            refresh = RefreshToken.for_user(serializer.instance)
            user_data = UserSerializer(serializer.instance).data
            return Response({
                'message': 'Congratulations! your account has been created successfully, also we have invited you select contacts',
                'succesLoggged': True,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        return Response({
            'succesLoggged': True,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data,
        })
    return Response({'error': 'Invalid Credentials'}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def generateWithInvitation(request):
    username = request.data.get('username')
    invitation_code = request.data.get('invitation_code')
    
    if not username or not invitation_code:
        return Response({'error': 'Username and invitation code are required.'}, status=400)
    
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return Response({'error': 'User not found.'}, status=404)

    try:
        Invitation.objects.get(user=user, invitation_code=invitation_code)
    except ObjectDoesNotExist:
        return Response({'error': 'Invalid invitation code.'}, status=400)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'succesLoggged': True,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserSerializer(user).data,
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f'{settings.FRONTEND_URL}/api/reset-password/{uid}/{token}/'

        # Prepare the email content with HTML format
        email_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Password Reset Request</title>
        </head>
        <body>
            <p>Hi {user.username},</p>
            <p>You have requested to reset your password. Please click the link below to reset your password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>If you did not request a password reset, please ignore this email.</p>
            <p>Thank you,</p>
            <p>Quick Snap Team</p>
        </body>
        </html>
        """

        # Prepare the email subject
        subject = 'Password Reset Request'

        # Send the email using the API function
        email_response = send_email_via_api(to_email=email, subject=subject, message=email_content)
        print(email_response)
        if email_response.get('success') == True:
            return Response({'message': 'Password reset link sent successfully.'})
        else:
            return Response({'error': 'Failed to send email.'}, status=500)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist.'}, status=404)

def reset_password_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponse("You have successfully reset your password now you can use in you mobile app to login.", status=400) # Redirect to login after password reset
        else:
            form = SetPasswordForm(user)
        return render(request, 'core/reset_password_confirm.html', {'form': form, "uidb64":uidb64, "token":token})
    else:
        return HttpResponse("Invalid token", status=400)

def create_notification(user, message):
    if isinstance(user, User):
        Notification.objects.create(user=user, message=message)
    else:
        for u in user:
            Notification.objects.create(user=u, message=message)

def log_activity(user, action, details=None):
    ActivityLog.objects.create(user=user, action=action, details=details)

def accept_invitation(request, invitation_code):
    # Retrieve the invitation using the provided code
    invitation = get_object_or_404(Invitation, invitation_code=invitation_code)

    if request.method == 'POST':
        form = AcceptInvitationForm(request.POST)
        if form.is_valid():
            # Create a new user using the form data
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Mark the invitation as accepted
            invitation.status = 'accepted'
            invitation.save()

            # Optionally, you can assign the user to the event or perform other actions here

            # Show a success message
            messages.success(request, 'You have successfully accepted the invitation and registered.')

            # Redirect to a success page or login page
            return HttpResponse("You have successfully accepted the invitation and registered. now you can use in you mobile app to login.", status=400) # Redirect to login after password reset
    else:
        form = AcceptInvitationForm(initial={'email': invitation.recipient_email})

    return render(request, 'core/accept_invitation.html', {'form': form, 'invitation': invitation})

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['user__id', 'name']
    search_fields = ['name', 'description', 'user__id']
    permission_classes = [IsAuthenticated]

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['tagged_users__username', 'location']
    search_fields = ['caption', 'location', 'tagged_users__username']
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Save the photo object
        photo = serializer.save()
        # Check if an image was uploaded
        if 'image' in self.request.FILES:
            image_file = self.request.FILES['image']
            cloud_url = upload_file_to_s3(image_file)

            # Decode the JSON string into a Python dictionary
            decoded_dict = cloud_url
            if cloud_url:
                photo.cloud_url = decoded_dict.get('data')
                photo.save()
        # Log the activity
        log_activity(photo.album.user, 'uploaded photo', {'photo_id': photo.id})

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'albums__id', 'user__id']
    search_fields = ['name', 'user__username', 'albums__name']
    permission_classes = [IsAuthenticated]

class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [IsAuthenticated]

class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        invitation = serializer.save(sender=self.request.user)
        create_notification(invitation.recipient_email, f'You have been invited to the event: {invitation.event.name}')
        log_activity(self.request.user, 'sent invitation', {'invitation_id': invitation.id})

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        comment = serializer.save()
        create_notification(comment.photo.album.user, f'New comment on your photo by {comment.user.username}')
        create_notification(comment.photo.tagged_users.all(),
                            f'You were tagged in a comment by {comment.user.username}')

class SharedAlbumViewSet(viewsets.ModelViewSet):
    queryset = SharedAlbum.objects.all()
    serializer_class = SharedAlbumSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        shared_album = serializer.save()
        message = f'Album "{shared_album.album.name}" shared with you by {shared_album.album.user.username}'
        create_notification(shared_album.shared_with, message)
        log_activity(shared_album.album.user, 'shared album', {'album_id': shared_album.album.id, 'shared_with': shared_album.shared_with.username})

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
