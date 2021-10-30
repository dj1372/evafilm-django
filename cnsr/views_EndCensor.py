from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from cnsr.models import EndAppCnsr
from movies.models import PlayList, Season, Episode
from django.forms import ModelForm
from cnsr.utiles import string_to_time as stt


class CnsrEndForm(ModelForm):
    class Meta:
        model = EndAppCnsr
        fields = ['s', 'e']


def get_episode(ed, pl, sn):
    playlist = PlayList.objects.get(pk=pl)
    season = Season.objects.get(playlist=playlist, name=sn)
    episode = Episode.objects.all().filter(season=season, playlist=playlist, index=ed).first()
    return episode


def EndCensor(request, playlist, season, episode_index):
    form = CnsrEndForm(request.POST or None)
    pl = playlist
    sn = season
    ed = episode_index
    episode = get_episode(ed, pl, sn)
    queryset = EndAppCnsr.objects.all().filter(episode=episode)
    context = {
        "pl": pl, "sn": sn, "ed": ed, "status": "Start",
        "episode": episode, "object_list": queryset, "form": form
    }

    if request.method == "POST":
        if form.is_valid():
            try:
                now_s = request.POST.get("s")
                now_e = request.POST.get("e")
                if int(stt(now_s)) != int(stt(now_e)):
                    if episode:
                        EndAppCnsr.objects.create(episode=episode, s=now_s, e=now_e)
                else:
                    pass
            except:
                pass
    return render(request, "cnsr_End.html", context)


def EndCensorEdit(request, playlist, season, episode_index, pk, error_status=None):
    pl = playlist
    sn = season
    ed = episode_index
    pk = pk
    es = error_status
    episode = get_episode(ed, pl, sn)
    queryset = get_object_or_404(EndAppCnsr, episode=episode, pk=pk)
    context = {
        "pl": pl, "sn": sn, "ed": ed, "pk": pk, "status": "End",
        "episode": episode, "object": queryset, "es": es,
    }

    form = CnsrEndForm(request.POST or None, instance=queryset)
    context["form"] = form

    if request.method == "POST":
        now_s = request.POST.get("s")
        now_e = request.POST.get("e")
        if int(stt(now_s)) > int(stt(now_e)):
            return redirect(reverse("EndCensorEdit", kwargs={
                "playlist": pl, "season": sn, "episode_index": ed, "pk": pk, "error_status": 2}))
        elif int(stt(now_s)) == int(stt(now_e)):
            return redirect(reverse("EndCensorEdit", kwargs={
                "playlist": pl, "season": sn, "episode_index": ed, "pk": pk, "error_status": 1}))
        else:
            form.save()
            return redirect(reverse("EndCensor", kwargs={"playlist": pl, "season": sn, "episode_index": ed}))
    return render(request, "cnsr_Edit.html", context)


def EndCensorDelete(request, playlist, season, episode_index, pk):
    pl = playlist
    sn = season
    ed = episode_index
    pk = pk
    episode = get_episode(ed, pl, sn)
    queryset = get_object_or_404(EndAppCnsr, episode=episode, pk=pk)
    context = {
        "pl": pl, "sn": sn, "ed": ed, "pk": pk, "status": "End",
        "episode": episode, "object": queryset,
    }

    if request.method == "POST":
        queryset.delete()
        return redirect(reverse("EndCensor", kwargs={"playlist": pl, "season": sn, "episode_index": ed}))

    return render(request, "cnsr_Delete.html", context)
