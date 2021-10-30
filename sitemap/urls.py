from django.urls import path
from django.contrib.sitemaps.views import sitemap
from sitemap import utility

app_name = "sitemap"

urlpatterns = [
	path('sitemap.xml', sitemap,{"sitemaps":utility.SiteMaps},name='django.contrib.sitemaps.views.sitemap'),
]