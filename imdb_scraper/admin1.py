from django.contrib import admin
from imdb_scraper.models import Imdb
from imdb_scraper.tasks import movie_view
from celery.result import AsyncResult
from evafilm.celery import app


class ImdbAdmin(admin.ModelAdmin):
    list_display = ['id', 'link', 'celery_id', 'status', 'is_done']
    list_filter = ['status', 'is_done']
    search_fields = ['id', 'link', 'celery_id']
    actions = ['update_status']

    def update_status(self, request, queryset):
        for data in queryset:
            if data.is_done != True:
                res = AsyncResult(str(data.celery_id), app=app)
                data.status = res.status
                if res.status == 'SUCCESS':
                    data.is_done = True
                data.save()

    update_status.short_description = "Update status"

    def save_model(self, request, obj, form, change):
        if obj.celery_id is None:
            task = movie_view.delay(obj.link)
            obj.celery_id = task.id
        else:
            pass
        super().save_model(request, obj, form, change)

admin.site.register(Imdb, ImdbAdmin)
