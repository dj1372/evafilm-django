from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from cnsr.models import StartAppCnsr
from movies.models import Episode, PlayList, Season
from cnsr.utiles import string_to_time as stt
from django.forms import ModelForm


class CnsrStartForm(ModelForm):
    class Meta:
        model = StartAppCnsr
        fields = ['e']


def get_episode(ed, pl, sn):
    playlist = PlayList.objects.get(pk=pl)
    season = Season.objects.get(playlist=playlist, name=sn)
    episode = Episode.objects.all().filter(season=season, playlist=playlist, index=ed).first()
    return episode


def StartCensor(request, playlist, season, episode_index):
    form = CnsrStartForm(request.POST or None)
    pl = playlist
    sn = season
    ed = episode_index
    episode = get_episode(ed, pl, sn)
    queryset = StartAppCnsr.objects.all().filter(episode=episode)
    context = {
        "pl": pl, "sn": sn, "ed": ed, "status": "Start",
        "episode": episode, "object_list": queryset, "form": form,
    }

    if request.method == "POST":
        if form.is_valid():
            try:
                now_e = request.POST.get("e")
                if int(stt(now_e)) != 0:
                    if episode:
                        StartAppCnsr.objects.create(episode=episode, e=now_e)
                else:
                    pass
            except:
                pass
    return render(request, "cnsr_Start.html", context)


def StartCensorEdit(request, playlist, season, episode_index, pk, error_status=None):
    pl = playlist
    sn = season
    ed = episode_index
    pk = pk
    es = error_status
    episode = get_episode(ed, pl, sn)
    queryset = get_object_or_404(StartAppCnsr, episode=episode, pk=pk)
    context = {
        "pl": pl, "sn": sn, "ed": ed, "pk": pk, "status": "Start",
        "episode": episode, "object": queryset, "es": es,
    }

    form = CnsrStartForm(request.POST or None, instance=queryset)
    context["form"] = form

    if request.method == "POST":
        now_e = request.POST.get("e")
        if int(stt(now_e)) != 0:
            form.save()
            return redirect(reverse("StartCensor", kwargs={"playlist": pl, "season": sn, "episode_index": ed}))
        else:
            return redirect(reverse("StartCensorEdit", kwargs={
                "playlist": pl, "season": sn, "episode_index": ed, "pk": pk, "error_status": 1}))
    return render(request, "cnsr_Edit.html", context)


def StartCensorDelete(request, playlist, season, episode_index, pk):
    pl = playlist
    sn = season
    ed = episode_index
    pk = pk
    episode = get_episode(ed, pl, sn)
    queryset = get_object_or_404(StartAppCnsr, episode=episode, pk=pk)
    context = {
        "pl": pl, "sn": sn, "ed": ed, "pk": pk, "status": "Start",
        "episode": episode, "object": queryset,
    }

    if request.method == "POST":
        queryset.delete()
        return redirect(reverse("StartCensor", kwargs={"playlist": pl, "season": sn, "episode_index": ed}))

    return render(request, "cnsr_Delete.html", context)
