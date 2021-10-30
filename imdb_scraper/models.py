from django.db import models


class Imdb(models.Model):
    link = models.CharField(max_length=500, verbose_name="لینک")
    celery_id = models.CharField(max_length=500, blank=True, null=True, verbose_name="شناسه")
    status = models.CharField(max_length=50, blank=True, null=True, verbose_name="وضعیت")
    log = models.TextField(max_length=10000, blank=True, null=True)
    is_done = models.BooleanField(default=False)


class ImdbScraperTest(models.Model):
    test_url = models.CharField(max_length=255, blank=True, null=True)
    TitleText = models.CharField(max_length=255, blank=True, null=True)
    TitleMetaDataContainer = models.CharField(max_length=255, blank=True, null=True)
    content_type_role = models.CharField(max_length=255, blank=True, null=True)
    ActorName = models.CharField(max_length=255, blank=True, null=True)
    rating = models.CharField(max_length=255, blank=True, null=True)
    TextContainerBreakpointXL = models.CharField(max_length=255, blank=True, null=True)
    director_a = models.CharField(max_length=255, blank=True, null=True)
    GenreChip = models.CharField(max_length=255, blank=True, null=True)
    hero_media_a = models.CharField(max_length=255, blank=True, null=True)
    TotalRatingAmount = models.CharField(max_length=255, blank=True, null=True)
    country_a = models.CharField(max_length=255, blank=True, null=True)
