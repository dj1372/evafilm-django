import string
import sys
import urllib.parse
from django.shortcuts import render
from os import error, name, stat
from django.contrib.auth.decorators import user_passes_test
from django import forms
from django.shortcuts import render
import requests
from requests import exceptions
from requests.api import get, head
from requests.models import HTTPError
from movies.models import PlayList, Actor, Season, Director, Episode, Country, Category
from .forms import GetLinkForm
from .forms import GetMultiLinkForm
from imdb_scraper.tasks import movie_view
from django.contrib.auth import get_user_model

User = get_user_model()


# @user_passes_test(lambda u: u.is_superuser)
def MovieView(request):
    if request.method == 'POST':
        form = GetLinkForm(request.POST)
        if form.is_valid():
            task = movie_view.delay(request.POST.get('url'))
            task.get()
        # movie_view.delay(request)

    form = GetLinkForm()
    form2 = GetMultiLinkForm()
    qs = PlayList.objects.all()
    movie_count = qs.count()
    act_qs = Actor.objects.all()
    actor_count = act_qs.count()

    context = {
        'qs': qs,
        'movie_count': movie_count,
        'form': form,
        'form2': form2,
        'actor_count': actor_count,
    }

    return render(request, 'imdb_scraper/main.html', context)
