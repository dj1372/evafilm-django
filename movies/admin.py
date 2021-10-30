from django.contrib import admin
from .models import Category, Actor, PlayList, Episode, Country, Contact, Season, Director

admin.site.register(Director)
admin.site.register(Country)
admin.site.register(Category)
admin.site.register(Actor)
admin.site.register(PlayList)
admin.site.register(Season)
admin.site.register(Episode)
admin.site.register(Contact)
