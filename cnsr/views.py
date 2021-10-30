# //////////////////////////////////// Show Error ///////////////////////////////////////////////

def ErrorWhenSave(request, playlist, season, episode_index, pk=None):
    context = {}

    pl = playlist
    context["pl"] = pl
    sn = season
    context["sn"] = sn
    ed = episode_index
    context["ed"] = ed
    pk = pk
    context["pk"] = pk

    return render(request, "Error_when_save.html", context)


# //////////////////////////////////// API ///////////////////////////////////////////////
from cnsr.models import StartAppCnsr, MiddelAppCnsr, EndAppCnsr
from cnsr.serializers import StartAppCnsrSerializers, MiddelAppCnsrSerializers, EndAppCnsrSerializers
from rest_framework import viewsets, permissions, status


class StartAppCnsrView(viewsets.ModelViewSet):
    queryset = StartAppCnsr.objects.all()
    serializer_class = StartAppCnsrSerializers
    permission_classes = [permissions.IsAdminUser]


class MiddelAppCnsrView(viewsets.ModelViewSet):
    queryset = MiddelAppCnsr.objects.all()
    serializer_class = MiddelAppCnsrSerializers
    permission_classes = [permissions.IsAdminUser]


class EndAppCnsrView(viewsets.ModelViewSet):
    queryset = EndAppCnsr.objects.all()
    serializer_class = EndAppCnsrSerializers
    permission_classes = [permissions.IsAdminUser]


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.shortcuts import reverse, render

from django.contrib.auth import get_user_model

User = get_user_model()


class ListS(APIView):
    """
    List all Censor
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        episode = kwargs.get("episode")
        my_list = {}
        Sepisode = StartAppCnsr.objects.all().filter(episode_id=episode)
        Mepisode = MiddelAppCnsr.objects.all().filter(episode_id=episode)
        Eepisode = EndAppCnsr.objects.all().filter(episode_id=episode)
        serializer_episodeS = StartAppCnsrSerializers(Sepisode, many=True)
        serializer_episodeM = MiddelAppCnsrSerializers(Mepisode, many=True)
        serializer_episodeE = EndAppCnsrSerializers(Eepisode, many=True)

        if not serializer_episodeS.data:
            my_list["ti"] = serializer_episodeS.data
        else:
            my_list["ti"] = serializer_episodeS.data[0]

        my_list["ce"] = serializer_episodeM.data

        if not serializer_episodeE.data:
            my_list["ne"] = serializer_episodeE.data
        else:
            my_list["ne"] = serializer_episodeE.data[0]

        return Response(my_list)

    # def post(self, request, *args, **kwargs):
    #     episode = kwargs.get("episode")
    #     my_list = {}
    #     Sepisode = StartAppCnsr.objects.all().filter(episode_id=episode)
    #     Mepisode = MiddelAppCnsr.objects.all().filter(episode_id=episode)
    #     Eepisode = EndAppCnsr.objects.all().filter(episode_id=episode)
    #     serializer_episodeS = StartAppCnsrSerializers(Sepisode, many=True)
    #     serializer_episodeM = MiddelAppCnsrSerializers(Mepisode, many=True)
    #     serializer_episodeE = EndAppCnsrSerializers(Eepisode, many=True)
    #
    #     if not serializer_episodeS.data:
    #         my_list["ti"] = serializer_episodeS.data
    #     else:
    #         my_list["ti"] = serializer_episodeS.data[0]
    #
    #     my_list["ce"] = serializer_episodeM.data
    #
    #     if not serializer_episodeE.data:
    #         my_list["ne"] = serializer_episodeE.data
    #     else:
    #         my_list["ne"] = serializer_episodeE.data[0]
    #
    #     if not (serializer_episodeS.data and serializer_episodeM.data and serializer_episodeE.data):
    #         return Response(
    #             serializer_episodeS.errors
    #             and serializer_episodeM.errors
    #             and serializer_episodeE.errors,
    #             status=status.HTTP_200_OK
    #         )
    #     else:
    #         return Response(my_list, status=status.HTTP_404_NOT_FOUND)
