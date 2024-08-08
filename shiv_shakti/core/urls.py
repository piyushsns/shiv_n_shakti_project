from django.urls import path, include
from .views import generateWithInvitation, SearchView
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, AlbumViewSet, PhotoViewSet, EventViewSet, GuestViewSet, InvitationViewSet, CommentViewSet, SharedAlbumViewSet, NotificationViewSet, ActivityLogViewSet, RegisterView, login
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'user-profiles', UserProfileViewSet)
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
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/generate', login, name='login'),
    path('token/generateWithInvitation', generateWithInvitation, name='generateWithInvitation'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += [
    path('search/', SearchView.as_view(), name='search'),
]