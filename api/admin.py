from django.contrib import admin
from api import models as api_models

admin.site.register(api_models.Comment)
admin.site.register(api_models.LikedPlayList)
admin.site.register(api_models.BookmarkPlayList)
admin.site.register(api_models.HistoryPlayList)
admin.site.register(api_models.VideoEdit)
