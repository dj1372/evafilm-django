from django.shortcuts import render, redirect
from admin_panel import forms as admin_forms
from movies import models as movies_models
from api import models as api_models
from django.contrib.auth import get_user_model


def playlists_view(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    if request.user.is_superuser:
        playlists = movies_models.PlayList.objects.all().order_by('-id')
    else:
        playlists = movies_models.PlayList.objects.filter(created_by=request.user).order_by('-id')

    return render(request, 'cpanel/playlists.html', {'playlists': playlists})


def new_playlist_view(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    if request.method == 'POST':
        form = admin_forms.NewMovieForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            if movies_models.PlayList.objects.filter(name_en=form.cleaned_data['name_en'],
                                                     name_fa=form.cleaned_data['name_fa']).count() == 0:
                form.save()
                playlist = movies_models.PlayList.objects.get(name_en=form.cleaned_data['name_en'],
                                                              name_fa=form.cleaned_data['name_fa'])
                playlist.created_by = request.user
                playlist.save()
            else:
                form = admin_forms.NewMovieForm
                return render(request, 'cpanel/new_playlist.html', {'form': form, 'msg': 1})
        else:
            return render(request, 'cpanel/new_playlist.html', {'msg': 2})
        return redirect('admin_playlists')

    elif request.method == 'GET':
        form = admin_forms.NewMovieForm
        return render(request, 'cpanel/new_playlist.html', {'form': form})


def edit_playlist_view(request, playlist):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    playlist = movies_models.PlayList.objects.get(pk=playlist)
    if request.method == 'POST':
        form = admin_forms.NewMovieForm(data=request.POST, files=request.FILES, instance=playlist)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'cpanel/new_playlist.html', {'msg': 2})
        return redirect('admin_playlists')

    elif request.method == 'GET':
        form = admin_forms.NewMovieForm(instance=playlist)
        return render(request, 'cpanel/new_playlist.html', {'form': form})


def delete_playlist_view(request, playlist):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    playlist = movies_models.PlayList.objects.get(pk=playlist)
    playlist.delete()
    return redirect('admin_playlists')


def new_episode_view(request, playlist, season):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    if request.method == 'POST':
        form = admin_forms.NewEpisodeForm(request.POST)
        if form.is_valid():
            if movies_models.Episode.objects.filter(season=form.cleaned_data['season'],
                                                    index=form.cleaned_data['index']).count() == 0:
                form.save()
            else:
                form = admin_forms.NewEpisodeForm
                return render(request, 'cpanel/new_episode.html', {'form': form, 'msg': 1})
        else:
            return render(request, 'cpanel/new_episode.html', {'msg': 2})
        return redirect('admin_episodes', playlist=playlist, season=season)

    elif request.method == 'GET':
        playlist = movies_models.PlayList.objects.get(pk=playlist)
        season = movies_models.Season.objects.get(playlist=playlist, name=season)
        form = admin_forms.NewEpisodeForm(initial={
            'playlist': playlist,
            'season': season,
            'index': playlist.Episodes.filter(playlist=playlist, season=season).count() + 1,
        })
        return render(request, 'cpanel/new_episode.html', {'form': form, 'playlist': playlist, 'season': season})


def episodes_view(request, playlist, season):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')
    playlist = movies_models.PlayList.objects.get(pk=playlist)
    season = movies_models.Season.objects.get(playlist=playlist, name=season)
    episodes = movies_models.Episode.objects.filter(playlist=playlist, season=season).order_by('-index').reverse()
    return render(request, 'cpanel/episodes.html', {'playlist': playlist, 'episodes': episodes, 'season': season})


def edit_episode_view(request, playlist, season, episode_index):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    if not request.user.is_authenticated:
        return redirect('Login')

    playlist = movies_models.PlayList.objects.get(pk=playlist)
    season = movies_models.Season.objects.get(playlist=playlist, name=season)
    episode = movies_models.Episode.objects.get(season=season, playlist=playlist, index=episode_index)
    if request.method == 'POST':
        form = admin_forms.NewEpisodeForm(request.POST, instance=episode)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'cpanel/new_episode.html', {'msg': 2})
        return redirect('admin_episodes', playlist=playlist.id, season=season.name)

    elif request.method == 'GET':
        form = admin_forms.NewEpisodeForm(instance=episode)
        return render(request, 'cpanel/new_episode.html', {'form': form, 'playlist': playlist, 'season': season})


def delete_episode_view(request, playlist, season, episode_index):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    playlist = movies_models.PlayList.objects.get(pk=playlist)
    season = movies_models.Season.objects.get(playlist=playlist, name=season)
    episode = movies_models.Episode.objects.get(playlist=playlist, season=season, index=episode_index)
    episode.delete()
    return redirect('admin_episodes', playlist=playlist.id, season=season.name)


def timing_episode_view(request, playlist, season, episode_index):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    if not request.user.is_authenticated:
        return redirect('Login')

    playlist = movies_models.PlayList.objects.get(pk=playlist)
    season = movies_models.Season.objects.get(playlist=playlist, name=season)
    episode = movies_models.Episode.objects.get(season=season, playlist=playlist, index=episode_index)
    if request.method == 'POST':
        form = admin_forms.TimingEpisodeForm(request.POST, instance=episode.Timing)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'cpanel/timing_episode.html', {'msg': 2})
        return redirect('admin_episodes', playlist=playlist.id, season=season.name)

    elif request.method == 'GET':
        form = admin_forms.TimingEpisodeForm(instance=episode.Timing)
        return render(request, 'cpanel/timing_episode.html', {'form': form, 'playlist': playlist, 'season': season,
                                                              'episode_index': episode.index})


def seasons_view(request, playlist):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    playlist = movies_models.PlayList.objects.get(pk=playlist)
    seasons = movies_models.Season.objects.filter(playlist=playlist).order_by('-name').reverse()
    return render(request, 'cpanel/seasons.html', {'seasons': seasons, 'playlist': playlist})


def new_season_view(request, playlist):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    if request.method == 'POST':
        form = admin_forms.NewSeasonForm(request.POST)
        if form.is_valid():
            if movies_models.Season.objects.filter(playlist=form.cleaned_data['playlist'],
                                                   name=form.cleaned_data['name']).count() == 0:
                form.save()
            else:
                form = admin_forms.NewSeasonForm
                return render(request, 'cpanel/new_episode.html', {'form': form, 'msg': 1})
        else:
            return render(request, 'cpanel/new_episode.html', {'msg': 2})
        return redirect('admin_seasons', playlist=playlist)

    elif request.method == 'GET':
        playlist = movies_models.PlayList.objects.get(pk=playlist)
        form = admin_forms.NewSeasonForm(initial={
            'playlist': playlist,
            'name': playlist.Seasons.count() + 1
        })
        return render(request, 'cpanel/new_season.html', {'form': form, 'playlist': playlist})


def edit_season_view(request, playlist, season):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    playlist = movies_models.PlayList.objects.get(pk=playlist)
    season = movies_models.Season.objects.get(name=season, playlist=playlist)

    if request.method == 'POST':
        form = admin_forms.NewSeasonForm(request.POST, instance=season)
        if form.is_valid():
            if movies_models.Season.objects.filter(playlist=form.cleaned_data['playlist'],
                                                   name=form.cleaned_data['name']).count() == 0:
                form.save()
            else:
                form = admin_forms.NewSeasonForm
                return render(request, 'cpanel/new_season.html', {'form': form, 'msg': 1})
        else:
            return render(request, 'cpanel/new_season.html', {'msg': 2})
        return redirect('admin_seasons', playlist=playlist.pk)

    elif request.method == 'GET':
        form = admin_forms.NewSeasonForm(instance=season)
        return render(request, 'cpanel/new_season.html', {'form': form, 'playlist': playlist, 'season': season})


def delete_season_view(request, playlist, season):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    playlist = movies_models.PlayList.objects.get(pk=playlist)
    season = movies_models.Season.objects.get(playlist=playlist, name=season)
    season.delete()
    return redirect('admin_seasons', playlist=playlist.pk)


def categories_view(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    categories = movies_models.Category.objects.all()
    return render(request, 'cpanel/categories.html', {'categories': categories})


def new_category_view(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    if request.method == 'POST':
        form = admin_forms.NewCategoryForm(request.POST)
        if form.is_valid():
            if movies_models.Category.objects.filter(name_en=form.cleaned_data['name_en'],
                                                     name_fa=form.cleaned_data['name_fa']).count() == 0:
                form.save()
            else:
                form = admin_forms.NewCategoryForm
                return render(request, 'cpanel/new_category.html', {'form': form, 'msg': 1})
        else:
            return render(request, 'cpanel/new_category.html', {'msg': 2})
        return redirect('admin_categories')

    elif request.method == 'GET':
        form = admin_forms.NewCategoryForm()
        return render(request, 'cpanel/new_category.html', {'form': form})


def edit_category_view(request, pk):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    category = movies_models.Category.objects.get(pk=pk)
    if request.method == 'POST':
        form = admin_forms.NewCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'cpanel/new_category.html', {'form': form, 'msg': 2})
        return redirect('admin_categories')

    elif request.method == 'GET':
        form = admin_forms.NewCategoryForm(instance=category)
        return render(request, 'cpanel/new_category.html', {'form': form})


def delete_category_view(request, pk):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    category = movies_models.Category.objects.get(pk=pk)
    category.delete()
    return redirect('admin_categories')


def directors_view(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    directors = movies_models.Director.objects.all().order_by('id')
    return render(request, 'cpanel/directors.html', {'directors': directors})


def new_director_view(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    if request.method == 'POST':
        form = admin_forms.NewDirectorForm(request.POST, files=request.FILES)
        if form.is_valid():
            if movies_models.Director.objects.filter(name=form.cleaned_data['name']).count() == 0:
                form.save()
            else:
                form = admin_forms.NewDirectorForm
                return render(request, 'cpanel/new_director.html', {'form': form, 'msg': 1})
        else:
            return render(request, 'cpanel/new_director.html', {'msg': 2})
        return redirect('admin_directors')

    elif request.method == 'GET':
        form = admin_forms.NewDirectorForm()
        return render(request, 'cpanel/new_director.html', {'form': form})


def edit_director_view(request, pk):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    actor = movies_models.Director.objects.get(pk=pk)
    if request.method == 'POST':
        form = admin_forms.NewDirectorForm(request.POST, files=request.FILES, instance=actor)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'cpanel/new_director.html', {'form': form, 'msg': 2})
        return redirect('admin_directors')

    elif request.method == 'GET':
        form = admin_forms.NewActorForm(instance=actor)
        return render(request, 'cpanel/new_director.html', {'form': form})


def delete_director_view(request, pk):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    actor = movies_models.Director.objects.get(pk=pk)
    actor.delete()
    return redirect('admin_directors')


def actors_view(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    actors = movies_models.Actor.objects.all().order_by('id')
    return render(request, 'cpanel/actors.html', {'actors': actors})


def new_actor_view(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    if request.method == 'POST':
        form = admin_forms.NewActorForm(request.POST, files=request.FILES)
        if form.is_valid():
            if movies_models.Actor.objects.filter(name=form.cleaned_data['name']).count() == 0:
                form.save()
            else:
                form = admin_forms.NewActorForm
                return render(request, 'cpanel/new_actor.html', {'form': form, 'msg': 1})
        else:
            return render(request, 'cpanel/new_actor.html', {'msg': 2})
        return redirect('admin_actors')

    elif request.method == 'GET':
        form = admin_forms.NewActorForm()
        return render(request, 'cpanel/new_actor.html', {'form': form})


def edit_actor_view(request, pk):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    actor = movies_models.Actor.objects.get(pk=pk)
    if request.method == 'POST':
        form = admin_forms.NewActorForm(request.POST, files=request.FILES, instance=actor)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'cpanel/new_actor.html', {'form': form, 'msg': 2})
        return redirect('admin_actors')

    elif request.method == 'GET':
        form = admin_forms.NewActorForm(instance=actor)
        return render(request, 'cpanel/new_actor.html', {'form': form})


def delete_actor_view(request, pk):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')

    actor = movies_models.Actor.objects.get(pk=pk)
    actor.delete()
    return redirect('admin_actors')


def redirect_cpanel(request):
    if (not request.user.is_authenticated) or (not request.user.is_staff):
        return redirect('Login')
    return redirect('https://evafilm.stream/cpanel/playlists/')
