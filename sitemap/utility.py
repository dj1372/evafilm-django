from django.contrib.sitemaps import Sitemap
from django.contrib import sitemaps
from django.urls import reverse
from movies.models import Category, Actor, PlayList, Episode, Country, Contact, Season, Director


class PlayListSitemap(Sitemap):
	changefreq = 'weekly'
	priority = 1

	def items(self):
		return PlayList.objects.all()

	def lastmod(self, obj):
		return obj.updated_at

		
class EpisodeSitemap(Sitemap):
	changefreq = 'weekly'
	priority = 1

	def items(self):
		return Episode.objects.all()


class ActorSitemap(Sitemap):
	changefreq = 'weekly'
	priority = 1

	def items(self):
		return Actor.objects.all()


class DirectorSitemap(Sitemap):
	changefreq = 'weekly'
	priority = 1

	def items(self):
		return Director.objects.all()


class ByCategorySitemap(Sitemap):
	changefreq = 'weekly'
	priority = 1

	def items(self):
		return Category.objects.all()


class StaticViewSitemap(sitemaps.Sitemap):
	changefreq = 'always'
	priority = 1

	def items(self):
		return ['Subscription', 'Signup', "Login", "ForgetPassword", 'Categories', "Contact", "AboutUs", "Internet", "Search", 'FAQ', 'Terms', 'Privacy', 'Movies', 'Series']

	def location(self, item):
		return reverse(item)


# ##############################################################
SiteMaps = {}


def add_to_sitemaps(key, value, flag=0):
	# add
	if flag == 0:
		SiteMaps[key] = value
	# update
	else:
		SiteMaps.update({key: value})



add_to_sitemaps('static', StaticViewSitemap)
add_to_sitemaps('PlayList', PlayListSitemap)
add_to_sitemaps('Episode', EpisodeSitemap)
add_to_sitemaps('Actor', ActorSitemap)
add_to_sitemaps('Director', DirectorSitemap)
add_to_sitemaps('Category', ByCategorySitemap)
