from django.urls import path, include
from .views import SearchView
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, AlbumViewSet, PhotoViewSet, EventViewSet, GuestViewSet, InvitationViewSet, CommentViewSet, SharedAlbumViewSet, NotificationViewSet, ActivityLogViewSet, RegisterView, login


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
    path('login/', login, name='login'),
]
urlpatterns += [
    path('search/', SearchView.as_view(), name='search'),
]