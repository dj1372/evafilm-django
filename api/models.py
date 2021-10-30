from django.db import models
from movies import models as movies_models
from django.dispatch import receiver
from django.db.models.signals import post_save
from persiantools.jdatetime import JalaliDate
from datetime import datetime

from django.contrib.auth import get_user_model

User = get_user_model()

like_choice = (
    (1, 'Like'),
    (0, 'Dislike')
)

comment_status_choice = (
    (0, 'Waiting for confirm'), (1, 'Confirmed')
)


def convert_month(date):
    date = date.split('/')
    day = date[2]
    month = date[1]
    year = date[0]
    if month == '01':
        month = 'فروردین'
    elif month == '02':
        month = 'اردیبهشت'
    elif month == '03':
        month = 'خرداد'
    elif month == '04':
        month = 'تیر'
    elif month == '05':
        month = 'مرداد'
    elif month == '06':
        month = 'شهریور'
    elif month == '07':
        month = 'مهر'
    elif month == '08':
        month = 'آبان'
    elif month == '09':
        month = 'آذر'
    elif month == '10':
        month = 'دی'
    elif month == '11':
        month = 'بهمن'
    elif month == '12':
        month = 'اسفند'
    date = day + ' ' + month + ' ' + year
    return date


class HistoryPlayList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='HistoryPlaylist')
    episode = models.ForeignKey(movies_models.Episode, on_delete=models.CASCADE)
    current_time = models.IntegerField(null=True, blank=True)  # seconds
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.user.username + ' - ' + self.episode.playlist.name_en


class BookmarkPlayList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='BookmarkPlaylist')
    playlist = models.ForeignKey(movies_models.PlayList, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + ' - ' + self.playlist.name_en


class LikedPlayList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='LikedPlaylist')
    playlist = models.ForeignKey(movies_models.PlayList, on_delete=models.CASCADE)
    liked = models.PositiveSmallIntegerField(choices=like_choice)

    def __str__(self):
        return self.user.username + ' - ' + self.playlist.name_en


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist = models.ForeignKey(movies_models.PlayList, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField(choices=comment_status_choice, default=0)
    is_reveal = models.BooleanField(default=False)
    date_shamsi = models.CharField(max_length=25, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.playlist.name_en + ' - ' + self.user.username + ' - ' + str(self.status)

    def save(self, *args, **kwargs):
        self.date = datetime.now().date()
        self.date_shamsi = convert_month(JalaliDate.today().strftime("%Y/%m/%d"))
        super().save(*args, **kwargs)


class VideoEdit(models.Model):
    episode = models.OneToOneField(movies_models.Episode, on_delete=models.CASCADE, related_name='Timing',
                                   verbose_name='اپیزود')
    titration_time = models.CharField(max_length=55, default='0:0', null=True, blank=True,
                                      verbose_name='تایم تیتر شروع اپیزود')

    censor_times = models.TextField(max_length=512, null=True, blank=True, verbose_name='تایم سانسور')

    def __str__(self):
        return self.episode.playlist.name_en

    def save(self, *args, **kwargs):
        if self.titration_time is None:
            self.titration_time = '0:0'
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.censor_times is None:
            self.censor_times = '0:0'
        super().save(*args, **kwargs)


@receiver(post_save, sender=movies_models.Episode)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        VideoEdit.objects.create(episode=instance)
