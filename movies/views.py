from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Category, Episode, PlayList, Contact, Actor, Country, Director
from api import models as api_models
from django.core.paginator import Paginator
from django import template
from evafilm.settings import CONTENT_URL, SITE_URL
from api.models import HistoryPlayList, LikedPlayList, BookmarkPlayList
import string
from datetime import datetime
from giftcard.utiles import get_access
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .serializers import PlayListApiSerializer, ActorApiSerializer
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny

from slider.models import SliderItem

from .forms import SearchForm
# ********************************
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

register = template.Library()


@register.filter
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)


def get_user_history_playlist_query(user):
    query = HistoryPlayList.objects.filter(user=user)
    result_query = query.first().episode.playlist
    for i in query:
        if i != query.first().episode.playlist:
            result_query += i.episode.playlist
    return result_query


def get_promo_playlist(playlist):
    playlist_categories = []
    for i in playlist.category.all():
        playlist_categories.append(i.id)
    promo_playlist = PlayList.objects.filter(category__in=playlist_categories).distinct().order_by('-id',
                                                                                                   '-users_score')
    promo_playlist = promo_playlist.exclude(id=playlist.id)[:10]
    return promo_playlist


def get_newest_playlist(user, total_rec):
    newest_playlist = PlayList.objects.order_by('-id')[:total_rec]
    return newest_playlist


def get_popular_playlist(user, total_rec):
    popular_playlist = PlayList.objects.order_by('-imdb_score', '-id')[:total_rec]
    return popular_playlist


def get_updated_series_playlist(total_rec):
    playlist_updated_series = PlayList.objects.filter(type=2).order_by('-updated_at')[:total_rec]
    return playlist_updated_series


def get_playlists(total_rec, category_name):
    category = Category.objects.get(page_url=category_name)
    playlist = PlayList.objects.filter(category=category).order_by('-id')[:total_rec]
    return playlist


def home(request):
    playlists_new = get_newest_playlist(request.user, 10)
    playlists_popular = get_popular_playlist(request.user, 10)
    playlist_updated_series = get_updated_series_playlist(10)
    playlist_2021 = PlayList.objects.filter(year=2021).order_by('-id')[:10]
    playlist_free = PlayList.objects.filter(is_free=True).order_by('-id')[:10]
    actors = Actor.objects.all()[:10]
    slider_items = SliderItem.objects.all().order_by('priority')
    # if request.user.is_authenticated:
    #     playlists_history = HistoryPlayList.objects.filter(user=request.user).order_by('-id')[:10]
    # else:
    #     playlists_history = None
    return render(request, 'home.html', {'content_url': CONTENT_URL,
                                         'playlists_new': playlists_new,
                                         # 'playlists_history': playlists_history,
                                         'playlists_popular': playlists_popular,
                                         'playlist_updated_series': playlist_updated_series,
                                         'playlist_2021': playlist_2021,
                                         'playlist_2020': PlayList.objects.filter(year=2020).order_by('-id')[:10],
                                         'playlist_action': get_playlists(10, 'action'),
                                         'playlist_crime': get_playlists(10, 'crime'),
                                         'playlist_scifi': get_playlists(10, 'sci-fi'),
                                         'playlist_comedy': get_playlists(10, 'comedy'),
                                         'playlist_free': playlist_free,
                                         'actors': actors,
                                         'slider_items': slider_items,
                                         })


def category_view(request, name_en):
    if name_en == 'new':
        playlist_list = get_newest_playlist(request.user, 300)
        title = 'جدیدترین ها'
    elif name_en == 'popular':
        playlist_list = get_popular_playlist(request.user, 300)
        title = 'پرطرفدارترین ها'
    elif name_en == 'updated-series':
        playlist_list = get_updated_series_playlist(300)
        title = 'سریال های بروز شده'
    elif name_en == 'free':
        playlist_list = PlayList.objects.filter(is_free=True).order_by('-id')[:300]
        title = 'پخش رایگان'
    else:
        category = Category.objects.get(page_url=name_en)
        title = category.name_fa
        playlist_list = PlayList.objects.filter(category=category).order_by('-updated_at')

    paginator = Paginator(playlist_list, 28)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    playlist = paginator.get_page(page_number)
    return render(request, 'movies.html', {'title': title,
                                           'playlist': playlist,
                                           'content_url': CONTENT_URL,

                                           })


def movie_view(request, pk, name_en, name_fa):
    playlist = PlayList.objects.get(pk=pk)
    is_this_playlist_liked = -1
    is_this_playlist_bookmarked = 0
    if request.user.is_authenticated:
        if LikedPlayList.objects.filter(playlist=playlist, user=request.user).count() > 0:
            liked_playlist = LikedPlayList.objects.get(playlist=playlist, user=request.user)
            is_this_playlist_liked = liked_playlist.liked

        if BookmarkPlayList.objects.filter(playlist=playlist, user=request.user).count() > 0:
            is_this_playlist_bookmarked = 1
        else:
            is_this_playlist_bookmarked = 0

    comments = api_models.Comment.objects.filter(playlist=playlist, status=1).order_by('-date')
    promo_playlist = get_promo_playlist(playlist)
    return render(request, 'playlist-info.html', {'playlist': playlist,
                                                  'promo_playlist': promo_playlist,
                                                  'comments': comments,
                                                  'content_url': CONTENT_URL,
                                                  'is_this_playlist_liked': is_this_playlist_liked,
                                                  'is_this_playlist_bookmarked': is_this_playlist_bookmarked,

                                                  })


def series_view(request, pk, name_en, name_fa):
    playlist = PlayList.objects.get(pk=pk)
    is_this_playlist_liked = -1
    is_this_playlist_bookmarked = 0
    if request.user.is_authenticated:
        if LikedPlayList.objects.filter(playlist=playlist, user=request.user).count() > 0:
            liked_playlist = LikedPlayList.objects.get(playlist=playlist, user=request.user)
            is_this_playlist_liked = liked_playlist.liked

        if BookmarkPlayList.objects.filter(playlist=playlist, user=request.user).count() > 0:
            is_this_playlist_bookmarked = 1
        else:
            is_this_playlist_bookmarked = 0

    comments = api_models.Comment.objects.filter(playlist=playlist, status=1).order_by('-date')
    promo_playlist = get_promo_playlist(playlist)
    return render(request, 'playlist-info.html', {'playlist': playlist,
                                                  'promo_playlist': promo_playlist,
                                                  'comments': comments,
                                                  'content_url': CONTENT_URL,
                                                  'is_this_playlist_liked': is_this_playlist_liked,
                                                  'is_this_playlist_bookmarked': is_this_playlist_bookmarked,

                                                  })


def animation_view(request, pk, name_en, name_fa):
    playlist = PlayList.objects.get(pk=pk)
    is_this_playlist_liked = -1
    is_this_playlist_bookmarked = 0
    if request.user.is_authenticated:
        if LikedPlayList.objects.filter(playlist=playlist, user=request.user).count() > 0:
            liked_playlist = LikedPlayList.objects.get(playlist=playlist, user=request.user)
            is_this_playlist_liked = liked_playlist.liked

        if BookmarkPlayList.objects.filter(playlist=playlist, user=request.user).count() > 0:
            is_this_playlist_bookmarked = 1
        else:
            is_this_playlist_bookmarked = 0

    comments = api_models.Comment.objects.filter(playlist=playlist, status=1).order_by('-date')
    promo_playlist = get_promo_playlist(playlist)
    return render(request, 'playlist-info.html', {'playlist': playlist,
                                                  'promo_playlist': promo_playlist,
                                                  'comments': comments,
                                                  'content_url': CONTENT_URL,
                                                  'is_this_playlist_liked': is_this_playlist_liked,
                                                  'is_this_playlist_bookmarked': is_this_playlist_bookmarked,

                                                  })


def bookmark_playlist_view(request):
    if not request.user.is_authenticated:
        query_params = ''
        if not request.META.get('HTTP_REFERER') is None:
            query_params += '?r=' + request.META.get('HTTP_REFERER')
            return redirect(reverse('Login') + query_params)
        else:
            return redirect('Login')
    playlist_list = api_models.BookmarkPlayList.objects.filter(user=request.user).order_by('-id')
    title = 'فیلم های نشان شده'
    paginator = Paginator(playlist_list, 28)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    special_playlist = paginator.get_page(page_number)
    return render(request, 'bookmarks.html', {'title': title,
                                              'special_playlist': special_playlist,
                                              'content_url': CONTENT_URL,

                                              })


def like_playlist_view(request):
    if not request.user.is_authenticated:
        query_params = ''
        if not request.META.get('HTTP_REFERER') is None:
            query_params += '?r=' + request.META.get('HTTP_REFERER')
            return redirect(reverse('Login') + query_params)
        else:
            return redirect('Login')
    playlist_list = api_models.LikedPlayList.objects.filter(user=request.user, liked=1).order_by('-id')
    title = 'فیلم های مورد علاقه شما'
    paginator = Paginator(playlist_list, 28)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    special_playlist = paginator.get_page(page_number)
    return render(request, 'bookmarks.html', {'title': title,
                                              'special_playlist': special_playlist,
                                              'content_url': CONTENT_URL,

                                              })


def history_playlist_view(request):
    if not request.user.is_authenticated:
        query_params = ''
        if not request.META.get('HTTP_REFERER') is None:
            query_params += '?r=' + request.META.get('HTTP_REFERER')
            return redirect(reverse('Login') + query_params)
        else:
            return redirect('Login')
    playlist_list = api_models.HistoryPlayList.objects.filter(user=request.user).order_by('-id')
    title = 'فیلم های دیده شده'
    paginator = Paginator(playlist_list, 28)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    special_playlist = paginator.get_page(page_number)
    return render(request, 'history.html', {'title': title,
                                            'special_playlist': special_playlist,
                                            'content_url': CONTENT_URL,

                                            })


def play_vid(request, pk):
    if request.user.is_authenticated:
        episode = Episode.objects.get(pk=pk)
        access = get_access(request=request, episode=episode)
        if episode.playlist.is_free or access is True:
            current_time = 0
            if HistoryPlayList.objects.filter(episode=episode, user=request.user).count() > 0:
                history_playlist = HistoryPlayList.objects.get(episode=episode, user=request.user)
                current_time = history_playlist.current_time

            return render(request, 'play-vid.html', {'episode': episode,
                                                     'content_url': CONTENT_URL,
                                                     'current_time': current_time,

                                                     })
        elif hasattr(request.user, 'SubscriptionPlan'):
            if request.user.SubscriptionPlan.end_date >= datetime.today().date():
                current_time = 0
                if HistoryPlayList.objects.filter(episode=episode, user=request.user).count() > 0:
                    history_playlist = HistoryPlayList.objects.get(episode=episode, user=request.user)
                    current_time = history_playlist.current_time

                return render(request, 'play-vid.html', {'episode': episode,
                                                         'content_url': CONTENT_URL,
                                                         'current_time': current_time,

                                                         })
            return redirect('Subscription')
        return redirect('Subscription')
    else:
        query_params = ''
        query_params += '?r=' + request.META.get('HTTP_REFERER')
        return redirect(reverse('Login') + query_params)


def actor_view(request, pk, name):
    actor = Actor.objects.get(pk=pk)
    title = actor.name
    playlist_list = PlayList.objects.filter(actor=actor).order_by('-year')
    paginator = Paginator(playlist_list, 28)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    playlist = paginator.get_page(page_number)
    return render(request, 'crew.html', {'title': title,
                                         'crew': actor,
                                         'playlist': playlist,
                                         'content_url': CONTENT_URL,

                                         })


def director_view(request, pk, name):
    director = Director.objects.get(pk=pk)
    title = director.name
    playlist_list = PlayList.objects.filter(director=director).order_by('-year')
    paginator = Paginator(playlist_list, 28)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    playlist = paginator.get_page(page_number)
    return render(request, 'crew.html', {'title': title,
                                         'crew': director,
                                         'playlist': playlist,
                                         'content_url': CONTENT_URL,

                                         })


def year_view(request, year):
    title = 'فیلم و سریال های سال ' + year
    playlist_list = PlayList.objects.filter(year=year).order_by('-id')
    paginator = Paginator(playlist_list, 28)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    playlist = paginator.get_page(page_number)
    return render(request, 'category.html', {'title': title,
                                             'playlist': playlist,
                                             'content_url': CONTENT_URL,

                                             })


def country_view(request, name):
    country = Country.objects.get(name=name)
    title = 'فیلم و سریال های محصول کشور ' + country.name
    playlist_list = PlayList.objects.filter(country=country).order_by('-id')
    paginator = Paginator(playlist_list, 28)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    playlist = paginator.get_page(page_number)
    return render(request, 'category.html', {'title': title,
                                             'playlist': playlist,
                                             'content_url': CONTENT_URL,

                                             })


def faq_view(request):
    return render(request, 'faq.html')


def terms_view(request):
    return render(request, 'terms.html')


def privacy_view(request):
    return render(request, 'privacy.html')


def about_view(request):
    return render(request, 'about_us.html')


def internet_view(request):
    return render(request, 'internet.html')


def search_view(request):
    return render(request, 'search.html')


def blog_view(request):
    if not request.user.is_authenticated:
        query_params = ''
        if not request.META.get('HTTP_REFERER') is None:
            query_params += '?r=' + request.META.get('HTTP_REFERER')
            return redirect(reverse('Login') + query_params)
        else:
            return redirect('Login')
    return render(request, 'blog.html')


def contact_view(request):
    # if not request.user.is_authenticated:
    #     query_params = ''
    #     if not request.META.get('HTTP_REFERER') is None:
    #         query_params += '?r=' + request.META.get('HTTP_REFERER')
    #         return redirect(reverse('Login') + query_params)
    #     else:
    #         return redirect('Login')
    if request.method == 'POST':
        name = request.POST.get('name')
        email_phone = request.POST.get('email') + ' (' + request.POST.get('phone') + ')'
        message = request.POST.get('message')
        contact_us_ob = Contact.objects.create(name=name, mobile_or_email=email_phone, message=message)
        contact_us_ob.save()
        return render(request, 'contact.html', {'msg': 1,
                                                })
    else:
        return render(request, 'contact.html')


def movies_list_view(request):
    title = 'لیست فیلم ها'
    playlist_list = PlayList.objects.filter(type=1).order_by('-updated_at')

    paginator = Paginator(playlist_list, 28)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    playlist = paginator.get_page(page_number)
    return render(request, 'movies.html', {'title': title,
                                           'playlist': playlist_list,
                                           'content_url': CONTENT_URL,

                                           })


def series_list_view(request):
    title = 'لیست سریال ها'
    playlist_list = PlayList.objects.filter(type=2).order_by('-updated_at')

    paginator = Paginator(playlist_list, 28)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    playlist = paginator.get_page(page_number)
    return render(request, 'movies.html', {'title': title,
                                           'playlist': playlist_list,
                                           'content_url': CONTENT_URL,

                                           })


def categories_view(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories, })


def play_box(request, pk):
    list = [
        "https://as3.cdn.asset.aparat.com/aparat-video/f25633298181fd83fa4fe41cf2f72dd223404550-480p.mp4?wmsAuthSign=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6IjkyOWNiNjk5MmEzZTlmOTc4MTNhNmRmMDhjYTE2Y2FmIiwiZXhwIjoxNjEyNDg5MzA2LCJpc3MiOiJTYWJhIElkZWEgR1NJRyJ9.GhkBoAYtcrEr4ZD2OQf87tnyP4BnWBBh9bs4WPKdCaM",
        "https://aspb1.cdn.asset.aparat.com/aparat-video/866ea8d40e835fba26f1db0704feee7418593479-480p.mp4?wmsAuthSign=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6ImQxODA5NzkzM2IyZjljZjU5YzEzMWE1N2NmODcxZmJiIiwiZXhwIjoxNjEyNDkxMDU5LCJpc3MiOiJTYWJhIElkZWEgR1NJRyJ9.sGpWr_iU3eYdL0qf-yRLuyg_XkDBGJ3an-rBw-SPIdQ",
        "https://as10.cdn.asset.aparat.com/aparat-video/2526dc8f8319907daac392194ec431f827613433-480p.mp4?wmsAuthSign=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6ImY3ZjBlNjA3YjZmNGZkMDk4OWI1ZjAxMWQ1Mjg1ZjQ4IiwiZXhwIjoxNjEyNDkwMzExLCJpc3MiOiJTYWJhIElkZWEgR1NJRyJ9.Bm4Hsr1o1TBOdYGbHx6WGZTxCCS0vK8G2ucJLr8uW3U",
        "https://as4.cdn.asset.aparat.com/aparat-video/0c0b5f3feaa2d4c4cb2fac7e8e85b44524084163-480p.mp4?wmsAuthSign=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6IjM2NGYyYWVkNjUxZjFkMjBlNDhhMmQzYjk2Y2NmYjkzIiwiZXhwIjoxNjEyNDgyNDkzLCJpc3MiOiJTYWJhIElkZWEgR1NJRyJ9.Vd2SzFWq2uYTX56yO2S1dkm4Slau_S0kfVDTOcLWQiQ",
        "https://aspb12.cdn.asset.aparat.com/aparat-video/789153f25290d3a69fc39bef8055519915682696-240p.mp4?wmsAuthSign=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6ImMxY2M3ZGNhOThlY2M4YTNjZDU2N2U3NDYwNTBhMTA0IiwiZXhwIjoxNjEyNDc4NjAyLCJpc3MiOiJTYWJhIElkZWEgR1NJRyJ9.eaOAWNH1ZlA3L0N24ky3KSHrsXpYbJ5PdmJ2qSsY_Hc",
    ]
    x = list[pk]
    return render(request, 'play_box.html', {'addres': x, })


def actor_page(request):
    actors = Actor.objects.all()
    return render(request, 'actorlist.html', {'actors': actors, })


def search_box(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('name_en', 'name_fa', 'summary')
            search_query = SearchQuery(query)
            results = PlayList.objects.annotate(search=search_vector,
                                                rank=SearchRank(search_vector, search_query)).filter(
                search=search_query).order_by('-rank')
    return render(request, 'searchbox.html', {'form': form, 'query': query, 'results': results})


class PlayListApiPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class PlayList_Category_Action_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=1).order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Adventure_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=2)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Animation_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=3)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Biography_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=4)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Comedy_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=5)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Crime_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=6)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Documentry_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=7)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Drama_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=8)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Family_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=9)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Fantasy_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=10)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Film_Noir_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=11)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Game_Show_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=12)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_History_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=13)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Horror_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=14)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Music_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=15)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Musical_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=16)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Mystery_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=17)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_News_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=18)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Reality_Tv_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=19)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Romance_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=20)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Sci_Fi_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=21)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Sport_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=22)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Talk_Show_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=23)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Thriller_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=24)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_War_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=25)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Category_Western_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(category__index=26)
    queryset.order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Evafilm_New_view(generics.ListAPIView):
    queryset = PlayList.objects.all().order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Year_2021_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(year=2021, type=1).order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Series_Updated_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(type=2).order_by('updated_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Is_Free_view(generics.ListAPIView):
    queryset = PlayList.objects.filter(is_free=True).order_by('created_at').reverse()
    serializer_class = PlayListApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)


class PlayList_Actor_view(generics.ListAPIView):
    queryset = Actor.objects.all().order_by('id')
    serializer_class = ActorApiSerializer
    pagination_class = PlayListApiPaginator
    permission_classes = [AllowAny]

    def get_paginated_response(self, data):
        return Response(data)
