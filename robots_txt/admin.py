from django.contrib import admin

from robots_txt.models import Robots


class RobotsAdmin(admin.ModelAdmin):
    list_display = ["value", "select_type"]
    list_filter = ['select_type', ]
    list_display_links = ["value"]
    list_editable = ["select_type", ]
    search_fields = ["value"]


admin.site.register(Robots, RobotsAdmin)
