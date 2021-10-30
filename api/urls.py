from django.urls import path
from movies.models import PlayList
from rest_framework.authtoken import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from api import views as api_views

urlpatterns = [
    path('search/', csrf_exempt(api_views.Search.as_view())),
    path('review/like/', csrf_exempt(api_views.LikeAPIView.as_view())),
    path('review/history/', csrf_exempt(api_views.HistoryPlaylistAPIView.as_view())),
    path('review/bookmark/', csrf_exempt(api_views.BookmarkPlaylistAPIView.as_view())),
    path('review/comment/', csrf_exempt(api_views.CommentAPIView.as_view())),
    path('episode-timing/', csrf_exempt(api_views.EpisodeTimingAPIView.as_view())),
    path('profile-censor/', csrf_exempt(api_views.ProfileCensorAPIView.as_view())),
]