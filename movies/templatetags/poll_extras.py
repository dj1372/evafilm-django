from django import template
from .. forms import SearchForm

register = template.Library()


@register.filter
def category_for(query_set, playlist_type):
    if playlist_type == 2:
        return query_set.filter(type=2).order_by('-id')[:10]
    else:
        return query_set.exclude(type=2).order_by('-id')[:10]


@register.filter
def check_for_playlists_in_category(query_set, playlist_type):
    if playlist_type == 2:
        if query_set.filter(type=2).count() == 0:
            return False
        else:
            return True
    else:
        if query_set.exclude(type=2).count() == 0:
            return False
        else:
            return True


@register.filter
def sort_episodes(query_set):
    return query_set.order_by('index')


@register.inclusion_tag('search_posts.html')
def search_posts():
    form = SearchForm()

    return {'form': form}