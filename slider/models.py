from django.db import models
from movies.models import PlayList


class SliderItem(models.Model):
    playlist = models.ForeignKey(PlayList, on_delete=models.CASCADE)
    priority = models.PositiveIntegerField(verbose_name="الویت", default=0)

    def __str__(self):
        return f"{self.priority}) {self.playlist.name_en} ({self.playlist.year})"
