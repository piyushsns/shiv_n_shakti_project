from rest_framework import viewsets, filters, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import UserProfile, Album, Photo, Event, Guest, Invitation, Comment, SharedAlbum, Notification, ActivityLog
from .serializers import UserSerializer, UserProfileSerializer, AlbumSerializer, PhotoSerializer, EventSerializer, \
    GuestSerializer, InvitationSerializer, CommentSerializer, SharedAlbumSerializer, NotificationSerializer, \
    ActivityLogSerializer
from haystack.query import SearchQuerySet
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from .models import InvitationCode

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

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

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
        valid_invitation = InvitationCode.objects.get(user=user, code=invitation_code)
    except ObjectDoesNotExist:
        return Response({'error': 'Invalid invitation code.'}, status=400)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'username': user.username,
        'email': user.email,
        'success': True,
    })

def create_notification(user, message):
    if isinstance(user, User):
        Notification.objects.create(user=user, message=message)
    else:
        for u in user:
            Notification.objects.create(user=u, message=message)


def log_activity(user, action, details=None):
    ActivityLog.objects.create(user=user, action=action, details=details)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'user__username']
    permission_classes = [IsAuthenticated]


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['caption', 'location', 'tagged_users__username']
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        photo = serializer.save()
        log_activity(photo.album.user, 'uploaded photo', {'photo_id': photo.id})

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [filters.SearchFilter]
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
        log_activity(shared_album.album.user, 'shared album',
                     {'album_id': shared_album.album.id, 'shared_with': shared_album.shared_with.username})


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]


class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
