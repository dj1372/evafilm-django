from django.db import models
from django.shortcuts import reverse
from movies.models import Episode


class CnsrManager(models.Manager):

    def get_objects_or_None(self, episode):
        try:
            obj = self.get_queryset().all().filter(active=True, episode=episode)
        except:
            return None
        return obj


class StartAppCnsr(models.Model):
    s = models.CharField(max_length=8, default="00:00:00", verbose_name='زمان شروع', unique=False)
    e = models.CharField(max_length=8, default="00:00:00", verbose_name='زمان پایان', null=True, blank=True, unique=False)
    episode = models.OneToOneField(Episode, on_delete=models.CASCADE, verbose_name='اپیزود', null=True, blank=True)
    active = models.BooleanField(default=True, verbose_name='فعال')

    objects = CnsrManager()

    def __str__(self):
        return f"{self.episode} cnsr ID: {self.pk}"

    def save(self, *args, **kwargs):
        self.s = "00:00:00"
        return super(StartAppCnsr, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("StartCensor", kwargs={
            "playlist": self.episode.playlist,
            "season": self.episode.season,
            "episode_index": self.episode.index,
        })

    class Meta():
        verbose_name = 'تیتراژ آغاز'
        verbose_name_plural = 'تیتراژ آغاز'
        ordering = ["episode__season__name", "episode__index"]


class MiddelAppCnsr(models.Model):
    s = models.CharField(max_length=8, default="00:00:00", verbose_name='زمان شروع')
    e = models.CharField(max_length=8, default="00:00:00", verbose_name='زمان پایان', null=True, blank=True)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, verbose_name='اپیزود', null=True, blank=False,
                                unique=False)
    active = models.BooleanField(default=True, verbose_name='فعال')

    objects = CnsrManager()

    def __str__(self):
        return f"{self.episode} cnsr ID: {self.pk}"

    def get_absolute_url(self):
        return reverse("MiddelCensor", kwargs={
            "playlist": self.episode.playlist,
            "season": self.episode.season,
            "episode_index": self.episode.index,
        })

    class Meta():
        verbose_name = 'تایم سانسور'
        verbose_name_plural = 'تایم سانسور'
        ordering = ["s", "e"]


class EndAppCnsr(models.Model):
    s = models.CharField(max_length=8, default="00:00:00", verbose_name='زمان شروع')
    e = models.CharField(max_length=8, default="00:00:00", verbose_name='زمان پایان', null=True, blank=True)
    episode = models.OneToOneField(Episode, on_delete=models.CASCADE, verbose_name='اپیزود', null=True, blank=False)
    active = models.BooleanField(default=True, verbose_name='فعال')

    objects = CnsrManager()

    def __str__(self):
        return f"{self.episode} cnsr ID: {self.pk}"

    def get_absolute_url(self):
        return reverse("EndCensor", kwargs={
            "playlist": self.episode.playlist,
            "season": self.episode.season,
            "episode_index": self.episode.index,
        })

    class Meta():
        verbose_name = 'تیتراژ پایان'
        verbose_name_plural = 'تیتراژ پایان'
        ordering = ["episode__season__name", "episode__index"]
