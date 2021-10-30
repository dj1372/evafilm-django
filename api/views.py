from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from movies.models import PlayList, Episode
from api import models as api_models
from .serializers import PlaylistSerializer
from accounts.models import UserProfile
from rest_framework import filters

from django.contrib.auth import get_user_model

User = get_user_model()


class Search(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = PlayList.objects.all()
    serializer_class = PlaylistSerializer
    http_method_names = ['get']
    filter_backends = [filters.SearchFilter]
    search_fields = ('name_en', 'name_fa')
    ordering_fields = '__all__'


class LikeAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(api_token=request.POST.get('token'))
        except:
            return Response({"is_successful": False, "message": "Invalid token!"}, status=status.HTTP_403_FORBIDDEN)

        playlist = PlayList.objects.get(id=request.POST.get('playlist'))
        # score_n = playlist.users_score_n
        # score_p = playlist.users_score_p
        liked = int(request.POST.get('liked'))
        reset = request.POST.get('reset')
        if reset == 'true':
            try:
                api_models.LikedPlayList.objects.get(user=user_profile.user, playlist=playlist).delete()
            except:
                pass
        try:
            liked_playlist_obj = api_models.LikedPlayList.objects.get(user=user_profile.user, playlist=playlist)
            liked_playlist_obj.liked = liked
            liked_playlist_obj.save()
        except:
            api_models.LikedPlayList.objects.create(user=user_profile.user, playlist=playlist, liked=liked)

        score_p = len(api_models.LikedPlayList.objects.filter(playlist=playlist, liked=1))
        score_n = len(api_models.LikedPlayList.objects.filter(playlist=playlist, liked=0))

        playlist.users_score = (score_p / (score_p + score_n)) * 10
        playlist.users_score_p = score_p
        playlist.users_score_n = score_n
        playlist.save()

        # if reset == 'true':
        #     try:
        #         liked_playlist_obj = api_models.LikedPlayList.objects.get(user=user_profile.user, playlist=playlist)
        #         if liked_playlist_obj.liked == 1:
        #             score_p -= 1
        #         else:
        #             score_n += 1
        #         api_models.LikedPlayList.objects.get(user=user_profile.user, playlist=playlist).delete()
        #     except:
        #         pass
        # try:
        #     liked_playlist_obj = api_models.LikedPlayList.objects.get(user=user_profile.user, playlist=playlist)
        #     liked_playlist_obj.liked = liked
        #     liked_playlist_obj.save()
        #
        #     if liked_playlist_obj.liked == 1:
        #         score_p += 1
        #     else:
        #         score_n -= 1
        # except:
        #     api_models.LikedPlayList.objects.create(user=user_profile.user, playlist=playlist, liked=liked)
        #     if liked == 1:
        #         score_p += 1
        #     else:
        #         score_n -= 1
        #
        # playlist.users_score = (score_p / (score_p + score_n)) * 10
        # playlist.users_score_p = score_p
        # playlist.users_score_n = score_n
        # playlist.save()
        return Response({"is_successful": True}, status=status.HTTP_200_OK)


class HistoryPlaylistAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(api_token=request.POST.get('token'))
            episode = Episode.objects.get(pk=request.POST.get('episode'))
            current_time = request.POST.get('current_time')

            if api_models.HistoryPlayList.objects.filter(user=user_profile.user, episode=episode).count() == 1:
                seen_episode_obj = api_models.HistoryPlayList.objects.get(user=user_profile.user, episode=episode)
                seen_episode_obj.current_time = current_time
                seen_episode_obj.save()
            else:
                api_models.HistoryPlayList.objects.create(user=user_profile.user, episode=episode,
                                                          current_time=current_time)

            return Response({"is_successful": True}, status=status.HTTP_200_OK)

        except:
            return Response({"is_successful": False, "message": "Invalid token!"}, status=status.HTTP_403_FORBIDDEN)


class BookmarkPlaylistAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(api_token=request.POST.get('token'))
        except:
            return Response({"is_successful": False, "message": "Invalid token!"}, status=status.HTTP_403_FORBIDDEN)

        playlist = PlayList.objects.get(id=request.POST.get('playlist'))
        added = request.POST.get('added')
        if api_models.BookmarkPlayList.objects.filter(user=user_profile.user, playlist=playlist).count() == 0:
            bookmark_playlist_obj = api_models.BookmarkPlayList.objects.create(user=user_profile.user,
                                                                               playlist=playlist)
            bookmark_playlist_obj.save()
        else:
            api_models.BookmarkPlayList.objects.get(user=user_profile.user, playlist=playlist).delete()

        return Response({"is_successful": True}, status=status.HTTP_200_OK)


class CommentAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(api_token=request.POST.get('token'))
        except:
            return Response({"is_successful": False, "message": "Invalid token!"}, status=status.HTTP_403_FORBIDDEN)

        playlist = PlayList.objects.get(id=request.POST.get('playlist'))
        comment = request.POST.get('comment')
        is_reveal = request.POST.get('is_reveal')

        if api_models.Comment.objects.filter(user=user_profile.user, playlist=playlist).count() == 0:
            if api_models.Comment.objects.filter(playlist=playlist).count() > 50:
                comment_obj = api_models.Comment.objects.last()
                comment_obj.delete()
            comment_obj = api_models.Comment.objects.create(user=user_profile.user, playlist=playlist, comment=comment,
                                                            is_reveal=is_reveal)
            comment_obj.save()

        return Response({"is_successful": True}, status=status.HTTP_200_OK)


class EpisodeTimingAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(api_token=request.POST.get('token'))
        except:
            return Response({"is_successful": False, "message": "Invalid token!"}, status=status.HTTP_403_FORBIDDEN)

        episode = Episode.objects.get(pk=request.POST.get('episode'))
        json_data = {}

        if episode.Timing.titration_time != '':
            start_time, end_time = episode.Timing.titration_time.split(':')
            json_data.update({"ti": {"s": start_time, "e": end_time}})
        else:
            json_data.update({"ti": None})

        if episode.playlist.Episodes.count() > episode.index:
            next_episode = Episode.objects.get(playlist=episode.playlist, season=episode.season,
                                               index=episode.index + 1)
            json_data.update({"ne": {"url": next_episode.page_url}})
        else:
            json_data.update({"ne": None})

        if episode.Timing.censor_times != '':
            alist = episode.Timing.censor_times.split('\r\n')
            blist = []
            for i in alist:
                blist.append(i)

            json_data_pre = []
            for i in blist:
                start_time, end_time = i.split(':')
                p = {"s": start_time, "e": end_time}
                print(p)
                json_data_pre.append(p)

            json_data.update({"ce": json_data_pre})
        else:
            json_data.update({"ce": None})

        return Response(json_data)


class ProfileCensorAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(api_token=request.POST.get('token'))
        except:
            return Response({"is_successful": False, "message": "Invalid token!"}, status=status.HTTP_403_FORBIDDEN)

        censor = request.POST.get('censor')
        profile = request.user.Profile
        if censor == '0':
            profile.is_censor_on = False
        else:
            profile.is_censor_on = True
        profile.save()

        return Response({"is_successful": True}, status=status.HTTP_200_OK)
