from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from cnsr.utiles import string_to_time as stt
from cnsr.models import MiddelAppCnsr
from django.forms import ModelForm
from movies.models import PlayList, Season, Episode


class CnsrMiddelForm(ModelForm):
	class Meta:
		model = MiddelAppCnsr
		fields = ['s', 'e']


def get_episode(ed, pl, sn):
	playlist = PlayList.objects.get(pk=pl)
	season = Season.objects.get(playlist=playlist, name=sn)
	episode = Episode.objects.all().filter(season=season, playlist=playlist, index=ed).first()
	return episode


def MiddelCensor(request, playlist, season, episode_index):
	form = CnsrMiddelForm(request.POST or None)
	pl = playlist
	sn = season
	ed = episode_index
	episode = get_episode(ed, pl, sn)
	queryset = MiddelAppCnsr.objects.all().filter(episode=episode)
	context = {
		"pl": pl, "sn": sn, "ed": ed, "status": "Start",
		"episode": episode, "object_list": queryset, "form": form
	}

	if request.method == "POST":
		if form.is_valid():
			now_s = request.POST.get("s")
			now_e = request.POST.get("e")
			try:
				queryset_last = queryset.order_by("id").last()
				queryset_first = queryset.order_by("id").first()
				last_s = queryset_last.s
				last_e = queryset_last.e
				first_s = queryset_first.s
				first_e = queryset_first.e
				if (int(stt(now_s)) > int(stt(last_e))) and (int(stt(now_e)) > (int(stt(now_s)) and int(stt(last_e)))):
					MiddelAppCnsr.objects.create(episode=episode, s=now_s, e=now_e)
				elif (int(stt(last_s)) < int(stt(now_e))) and  (int(stt(now_e)) < int(stt(first_e))):
					MiddelAppCnsr.objects.create(episode=episode, s=now_s, e=now_e)
				elif (int(stt(now_e)) < int(stt(last_s))):
					MiddelAppCnsr.objects.create(episode=episode, s=now_s, e=now_e)
				else:
					return redirect(reverse("Error", kwargs={"playlist": pl, "season": sn, "episode_index": ed}))
			except:
				if int(stt(now_s)) != int(stt(now_e)):
					if episode:
						MiddelAppCnsr.objects.create(episode=episode, s=now_s, e=now_e)
				else:
					return redirect(reverse("Error", kwargs={"playlist": pl, "season": sn, "episode_index": ed}))

	return render(request, "cnsr_Middel.html", context)


def MiddelCensorEdit(request, playlist, season, episode_index, pk, error_status=None):
	pl = playlist
	sn = season
	ed = episode_index
	pk = pk
	es = error_status
	episode = get_episode(ed, pl, sn)
	queryset = MiddelAppCnsr.objects.all().filter(episode=episode, pk=pk)
	querysets = MiddelAppCnsr.objects.all().filter(episode=episode).order_by("id")
	context = {
		"pl": pl, "sn": sn, "ed": ed, "pk": pk, "status": "Middel",
		"episode": episode, "object": queryset[0], "es": es,
	}

	form = CnsrMiddelForm(request.POST or None, instance=queryset[0])
	context["form"] = form

	if request.method == "POST":
		now_s = request.POST.get("s")
		now_e = request.POST.get("e")
		try:
			p = Paginator(querysets, 1)
			queryset_last = p.page(p.count - 1).object_list[0]
			queryset_self = p.page(p.count).object_list[0]
			last_s = queryset_last.s
			last_e = queryset_last.e
			self_s = queryset_self.s
			self_e = queryset_self.e
			if (int(stt(now_s)) > int(stt(last_e))) and (int(stt(now_e)) > (int(stt(now_s)) and int(stt(last_e)))):
				form.save()
				return redirect(reverse("MiddelCensor", kwargs={"playlist": pl, "season": sn, "episode_index": ed}))
			elif int(stt(now_s)) < (int(stt(self_e)) and int(stt(now_e))):
				form.save()
				return redirect(reverse("MiddelCensor", kwargs={"playlist": pl, "season": sn, "episode_index": ed}))
			if int(stt(now_s)) > int(stt(now_e)):
				return redirect(reverse("MiddelCensorEdit", kwargs={
					"playlist": pl, "season": sn, "episode_index": ed, "pk": pk, "error_status": 2}))
			elif int(stt(now_s)) == int(stt(now_e)):
				return redirect(reverse("MiddelCensorEdit", kwargs={
					"playlist": pl, "season": sn, "episode_index": ed, "pk": pk, "error_status": 1}))
			else:
				return redirect(
					reverse("ErrorEdit", kwargs={"playlist": pl, "season": sn,
												 "episode_index": ed, "pk": pk}))
		except:
			pass

	return render(request, "cnsr_Edit.html", context)


def MiddelCensorDelete(request, playlist, season, episode_index, pk):
	pl = playlist
	sn = season
	ed = episode_index
	pk = pk
	episode = get_episode(ed, pl, sn)
	queryset = get_object_or_404(MiddelAppCnsr, episode=episode, pk=pk)
	context = {
		"pl": pl, "sn": sn, "ed": ed, "pk": pk, "status": "Middel",
		"episode": episode, "object": queryset,
	}

	if request.method == "POST":
		queryset.delete()
		return redirect(reverse("MiddelCensor", kwargs={"playlist": pl, "season": sn, "episode_index": ed}))

	return render(request, "cnsr_Delete.html", context)
