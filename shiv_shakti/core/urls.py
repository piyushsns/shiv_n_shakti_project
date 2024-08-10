from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.utils import send_test_email
from .views import (accept_invitation, generateWithInvitation, reset_password,
    reset_password_confirm, SearchView)
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, AlbumViewSet, PhotoViewSet, EventViewSet, GuestViewSet, InvitationViewSet, CommentViewSet, SharedAlbumViewSet, NotificationViewSet, ActivityLogViewSet, login, RegistrationUserViewSet

from rest_framework_simplejwt.views import TokenRefreshView
from .views import generateWithInvitation, reset_password, SearchView
from .views import UserProfileViewSet, AlbumViewSet, PhotoViewSet, EventViewSet, GuestViewSet, InvitationViewSet, CommentViewSet, SharedAlbumViewSet, NotificationViewSet, ActivityLogViewSet, RegisterView, login


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

    path('api/', include(router.urls)),  # Include API router
    path('register/', RegisterView.as_view(), name='register'),  # Register view
    path('token/generate', login, name='login'),  # Token generation view
    path('token/generateWithInvitation', generateWithInvitation, name='generateWithInvitation'),  # Token generation with invitation view
    path('password/reset/', reset_password, name='reset_password'),  # Password reset view
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Token refresh view
    path('', views.index_view, name='index'),  # Index page using function-based view
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),  # Privacy policy page using function-based view
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('services/', views.services, name='services'),
    path('testmail', send_test_email),
    path('accept-invitation/<str:invitation_code>/', accept_invitation, name='accept-invitation'),


]


urlpatterns += [
    path('search/', SearchView.as_view(), name='search'),
]