from django.db import models


class Imdb(models.Model):
    link = models.CharField(max_length=500, verbose_name="لینک")
    celery_id = models.CharField(max_length=500, blank=True, null=True, verbose_name="شناسه")
    status = models.CharField(max_length=50, blank=True, null=True, verbose_name="وضعیت")
    is_done = models.BooleanField(default=False)
