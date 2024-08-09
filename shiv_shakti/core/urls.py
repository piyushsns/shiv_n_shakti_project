from django.urls import path, include
from core.utils import send_test_email
from .views import (accept_invitation, generateWithInvitation, reset_password,
    reset_password_confirm, SearchView)
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, AlbumViewSet, PhotoViewSet, EventViewSet, GuestViewSet, InvitationViewSet, CommentViewSet, SharedAlbumViewSet, NotificationViewSet, ActivityLogViewSet, login, RegistrationUserViewSet
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'user-profiles', UserProfileViewSet)
router.register(r'resgister', RegistrationUserViewSet)
router.register(r'albums', AlbumViewSet)
router.register(r'photos', PhotoViewSet)
router.register(r'events', EventViewSet)
router.register(r'guests', GuestViewSet)
router.register(r'invitations', InvitationViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'shared-albums', SharedAlbumViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'activity-logs', ActivityLogViewSet)

urlpatterns = [
    path('testmail', send_test_email),
    path('', include(router.urls)),
    path('token/generate', login, name='login'),
    path('token/generateWithInvitation', generateWithInvitation, name='generateWithInvitation'),
    path('password/reset/', reset_password, name='reset_password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reset-password/<uidb64>/<token>/', reset_password_confirm, name='password_reset_confirm'),
    path('accept-invitation/<str:invitation_code>/', accept_invitation, name='accept-invitation'),
]

urlpatterns += [
    path('search/', SearchView.as_view(), name='search'),
]