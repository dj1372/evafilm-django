from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views
from movies import views as movies_views
from payments import views as payments_views
from admin_panel import views as admin_views
from django.contrib.auth import views as django_auth_views
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt
from imdb_scraper import views as imdb
from giftcard.views import Gift_Cart_View
from cnsr.views_StartCensor import (StartCensor, StartCensorEdit, StartCensorDelete)
from cnsr.views_EndCensor import (EndCensor, EndCensorEdit, EndCensorDelete)
from cnsr.views_MiddelCensor import (MiddelCensor, MiddelCensorEdit, MiddelCensorDelete)
from cnsr.views import ErrorWhenSave
from invitor.views import invitation_code_insert_view
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [

    # redirect blog #
    path('blog', RedirectView.as_view(url='http://evanews.ir/blog')),

    # path  to template for invitation test
    path('inv/', invitation_code_insert_view),
    # payment url
    path('subscription/', payments_views.subscription_view.as_view(), name='Subscription'),
    path("subscription_plan/<plan_name>/", payments_views.check_discount_code, name="check_discount_code"),
    path('subscription/confirm/', payments_views.subscription_payment_create, name='SubscriptionConfirm'),

    path('subscription/callback/melli/<int:order_id>/',
         csrf_exempt(payments_views.subscription_payment_callback_melli_view),
         name='subscribe_payment_callback_melli'),

    path('subscription/callback/mellat/<int:order_id>/',
         csrf_exempt(payments_views.subscription_payment_callback_mellat_view),
         name='subscribe_payment_callback_mellat'),

    path('subscription/callback/zarinpal/', csrf_exempt(payments_views.subscription_payment_callback_zarinpal_view),
         name='subscribe_payment_callback_zarinpall'),
    # end payment url
    path("gift-card/<int:status>/", Gift_Cart_View.as_view(), name="gift"),

    # path('api/', include('rest_framework.urls')),

    # cnsr api
    path("Censor/api/", include("cnsr.urls", namespace="cnsr_api")),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Start app cnsr add edit delet
    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/start/", StartCensor,
         name="StartCensor"),
    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/start/edit/<int:pk>/<int:error_status>",
         StartCensorEdit, name="StartCensorEdit"),
    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/start/delete/<int:pk>/", StartCensorDelete,
         name="StartCensorDelete"),

    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/middel/", MiddelCensor, name="MiddelCensor"),
    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/middel/edit/<int:pk>/<int:error_status>",
         MiddelCensorEdit,
         name="MiddelCensorEdit"),
    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/middel/delete/<int:pk>/", MiddelCensorDelete,
         name="MiddelCensorDelete"),

    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/end/", EndCensor, name="EndCensor"),
    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/end/edit/<int:pk>/<int:error_status>", EndCensorEdit,
         name="EndCensorEdit"),
    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/end/delete/<int:pk>/", EndCensorDelete,
         name="EndCensorDelete"),

    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/middel/error/<int:pk>/", ErrorWhenSave,
         name="ErrorEdit"),
    path("Censor/<int:playlist>/<int:season>/<int:episode_index>/middel/error/", ErrorWhenSave, name="Error"),
    # End app cnsr add edit delet

    path('admin/', admin.site.urls),

    path('', movies_views.home, name='Home'),
    path('signup/', accounts_views.signup_view, name='Signup'),
    path('logout/', django_auth_views.LogoutView.as_view(), name='Logout'),
    path('login/', accounts_views.login_view, name='Login'),
    # path('login-phone/', accounts_views.login_phone, name='LoginPhone'),

    path('addmovie/', imdb.MovieView, name='scrape_view'),

    path('forget-password/', accounts_views.forget_password_view, name='ForgetPassword'),
    path('change-password/', accounts_views.change_pass, name='ChangePassword'),
    path('change-name/', accounts_views.change_name, name='ChangeName'),
    path('change-email/', accounts_views.change_email, name='ChangeEmail'),
    path('edit-profile/', accounts_views.edit_profile, name='EditProfile'),
    path('profile/', accounts_views.profile, name='Profile'),
    path('profile/censor-status/', accounts_views.profile_censor_change, name="CensorStatus"),
    path('orderlist/', accounts_views.order_list, name='OrderList'),

    path('faq/', movies_views.faq_view, name='FAQ'),
    path('terms/', movies_views.terms_view, name='Terms'),
    path('privacy/', movies_views.privacy_view, name='Privacy'),
    path('contact/', movies_views.contact_view, name='Contact'),
    path('aboutus/', movies_views.about_view, name='AboutUs'),
    path('internet/', movies_views.internet_view, name='Internet'),
    path('search/', movies_views.search_view, name='Search'),
    path('actor_page', movies_views.actor_page, name='actor_page'),  # ***********
    path('search_engin', movies_views.search_box, name='search_page'),  # *search
    path('play_box/<int:pk>', movies_views.play_box, name='play_box'),

    path('tag/<str:name_en>/', movies_views.category_view, name='ByCategory'),
    path('movie/<int:pk>/<str:name_en>/<str:name_fa>/', movies_views.movie_view, name="playlist"),
    path('series/<int:pk>/<str:name_en>/<str:name_fa>/', movies_views.series_view, name="playlist"),
    path('actor/<int:pk>/<str:name>/', movies_views.actor_view, name='ViewActor'),
    path('director/<int:pk>/<str:name>/', movies_views.director_view, name='ViewDirector'),
    path('year/<str:year>/', movies_views.year_view, name='ByYear'),
    path('country/<str:name>/', movies_views.country_view, name='ByCountry'),
    path('p/<int:pk>/', movies_views.play_vid, name="episode"),
    path('bookmark/', movies_views.bookmark_playlist_view, name='Bookmark'),
    path('like/', movies_views.like_playlist_view, name='Like'),
    path('history/', movies_views.history_playlist_view, name='History'),
    path('movies/', movies_views.movies_list_view, name='Movies'),
    path('series/', movies_views.series_list_view, name='Series'),
    path('category', movies_views.categories_view, name='Categories'),

    path('api/v1/', include('api.urls')),
    path('api/playlist/', include('movies.urls')),

    # path('subscription/', payments_views.subscription_view, name='Subscription'),
    # path('subscription/confirm/', payments_views.subscription_payment_create, name='SubscriptionConfirm'),
    # path('subscription/callback/<str:order_id>/', csrf_exempt(payments_views.subscription_payment_callback_view),
    #      name='subscribe_payment_callback'),
    # path('subscription/callback/melli/<str:order_id>/', csrf_exempt(payments_views.subscription_payment_callback_melli_view),
    #      name='subscribe_payment_callback_melli'),
    # path('subscription/callback/mellat/<str:order_id>/', csrf_exempt(payments_views.subscription_payment_callback_mellat_view),
    #      name='subscribe_payment_callback_mellat'),
    # path('subscription/callback/zarinpal/<str:order_id>/', csrf_exempt(payments_views.subscription_payment_callback_zarinpal_view),
    #      name='subscribe_payment_callback_zarinpal'),

    path('cpanel/categories/', admin_views.categories_view, name='admin_categories'),
    path('cpanel/categories/new/', admin_views.new_category_view, name='admin_new_category'),
    path('cpanel/categories/<int:pk>/edit/', admin_views.edit_category_view, name='admin_edit_category'),
    path('cpanel/categories/<int:pk>/delete/', admin_views.delete_category_view, name='admin_delete_category'),

    path('cpanel/actors/', admin_views.actors_view, name='admin_actors'),
    path('cpanel/actors/new/', admin_views.new_actor_view, name='admin_new_actor'),
    path('cpanel/actors/<int:pk>/edit/', admin_views.edit_actor_view, name='admin_edit_actor'),
    path('cpanel/actors/<int:pk>/delete/', admin_views.delete_actor_view, name='admin_delete_actor'),

    path('cpanel/directors/', admin_views.directors_view, name='admin_directors'),
    path('cpanel/directors/new/', admin_views.new_director_view, name='admin_new_director'),
    path('cpanel/directors/<int:pk>/edit/', admin_views.edit_director_view, name='admin_edit_director'),
    path('cpanel/directors/<int:pk>/delete/', admin_views.delete_director_view, name='admin_delete_director'),

    path('cpanel/playlists/', admin_views.playlists_view, name='admin_playlists'),
    path('cpanel/playlists/new/', admin_views.new_playlist_view, name='admin_new_playlist'),
    path('cpanel/playlists/<int:playlist>/edit/', admin_views.edit_playlist_view, name='admin_edit_playlist'),
    path('cpanel/playlists/<int:playlist>/delete/', admin_views.delete_playlist_view, name='admin_delete_playlist'),

    path('cpanel/playlists/<int:playlist>/', admin_views.seasons_view, name='admin_seasons'),
    path('cpanel/playlists/<int:playlist>/new/', admin_views.new_season_view,
         name='admin_new_season'),
    path('cpanel/playlists/<int:playlist>/<int:season>/edit/', admin_views.edit_season_view,
         name='admin_edit_season'),
    path('cpanel/playlists/<int:playlist>/<int:season>/delete/', admin_views.delete_season_view,
         name='admin_delete_season'),

    path('cpanel/playlists/<int:playlist>/<int:season>/', admin_views.episodes_view,
         name='admin_episodes'),
    path('cpanel/playlists/<int:playlist>/<int:season>/new/', admin_views.new_episode_view,
         name='admin_new_episode'),
    path('cpanel/playlists/<int:playlist>/<int:season>/<int:episode_index>/edit/', admin_views.edit_episode_view,
         name='admin_edit_episode'),
    path('cpanel/playlists/<int:playlist>/<int:season>/<int:episode_index>/delete/', admin_views.delete_episode_view,
         name='admin_delete_episode'),

    path('cpanel/playlists/<int:playlist>/<int:season>/<int:episode_index>/timing/', admin_views.timing_episode_view,
         name='admin_timing_episode'),

    path('cpanel/', admin_views.redirect_cpanel, name='redirect_cpanel'),

    path('', include("robots_txt.urls", namespace="robots_txt")),
    path('', include("sitemap.urls", namespace="sitemap")),

    # last_position app
    path('', include('videoposition.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
