from django.urls import path
from movies.models import PlayList
from rest_framework.authtoken import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from movies import views as movies_views

urlpatterns = [
    # category index=1
    path('action/', csrf_exempt(movies_views.PlayList_Category_Action_view.as_view())),
    # category index=2
    path('adventure/', csrf_exempt(movies_views.PlayList_Category_Adventure_view.as_view())),
    # category index=3
    path('animation/', csrf_exempt(movies_views.PlayList_Category_Animation_view.as_view())),
    # category index=4
    path('biography/', csrf_exempt(movies_views.PlayList_Category_Biography_view.as_view())),
    # category index=5
    path('comedy/', csrf_exempt(movies_views.PlayList_Category_Comedy_view.as_view())),
    # category =6
    path('crime/', csrf_exempt(movies_views.PlayList_Category_Crime_view.as_view())),
    # category index=7
    path('documentry/', csrf_exempt(movies_views.PlayList_Category_Documentry_view.as_view())),
    # category index=8
    path('drama/', csrf_exempt(movies_views.PlayList_Category_Drama_view.as_view())),
    # category index=9
    path('family/', csrf_exempt(movies_views.PlayList_Category_Family_view.as_view())),
    # category index=10
    path('fantasy/', csrf_exempt(movies_views.PlayList_Category_Fantasy_view.as_view())),
    # category index=11
    path('film_noir/', csrf_exempt(movies_views.PlayList_Category_Film_Noir_view.as_view())),
    # category index=12
    path('game_show/', csrf_exempt(movies_views.PlayList_Category_Game_Show_view.as_view())),
    # category index=13
    path('history/', csrf_exempt(movies_views.PlayList_Category_History_view.as_view())),
    # category index=14
    path('horror/', csrf_exempt(movies_views.PlayList_Category_Horror_view.as_view())),
    # category index=15
    path('music/', csrf_exempt(movies_views.PlayList_Category_Music_view.as_view())),
    # category index=16
    path('musical/', csrf_exempt(movies_views.PlayList_Category_Musical_view.as_view())),
    # category index=17
    path('mystery/', csrf_exempt(movies_views.PlayList_Category_Mystery_view.as_view())),
    # category index=18
    path('news/', csrf_exempt(movies_views.PlayList_Category_News_view.as_view())),
    # category index=19
    path('reality_tv/', csrf_exempt(movies_views.PlayList_Category_Reality_Tv_view.as_view())),
    # category index=20
    path('romance/', csrf_exempt(movies_views.PlayList_Category_Romance_view.as_view())),
    # category index=21
    path('sci_fi/', csrf_exempt(movies_views.PlayList_Category_Sci_Fi_view.as_view())),
    # category index=22
    path('sport/', csrf_exempt(movies_views.PlayList_Category_Sport_view.as_view())),
    # category index=23
    path('talk_show/', csrf_exempt(movies_views.PlayList_Category_Talk_Show_view.as_view())),
    # category index=24
    path('thriller/', csrf_exempt(movies_views.PlayList_Category_Thriller_view.as_view())),
    # category index=25
    path('war/', csrf_exempt(movies_views.PlayList_Category_War_view.as_view())),
    # category index=26
    path('western/', csrf_exempt(movies_views.PlayList_Category_Western_view.as_view())),
    # category can show free
    path('free/', csrf_exempt(movies_views.PlayList_Is_Free_view.as_view())),
    # list of all actor
    path('actor/', csrf_exempt(movies_views.PlayList_Actor_view.as_view())),
    # list of all movie order by creation date
    path('new/', csrf_exempt(movies_views.PlayList_Evafilm_New_view.as_view())),
    # list of 2021 movie
    path('2021/', csrf_exempt(movies_views.PlayList_Year_2021_view.as_view())),
    # list of updated series
    path('series/', csrf_exempt(movies_views.PlayList_Series_Updated_view.as_view())),

]
