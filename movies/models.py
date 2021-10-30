from django.db import models
from django.contrib.auth.models import User
import random
import os
from datetime import datetime
from PIL import Image
from django.conf import settings
from django.shortcuts import reverse

from django.contrib.auth import get_user_model

User = get_user_model()

season_choice = (
    (0, 'انتخاب نشده'), (1, 'فصل 1'), (2, 'فصل 2'), (3, 'فصل 3'), (4, 'فصل 4'), (5, 'فصل 5'), (6, 'فصل 6')
    , (7, 'فصل 7'), (8, 'فصل 8'), (9, 'فصل 9'), (10, 'فصل 10'), (11, 'فصل 11'), (12, 'فصل 12')
)

type_choice = (
    (1, 'فیلم'), (2, 'سریال')
)

tv_pg_choice = (
    (1, 'زیر سه سال'), (3, '3 تا 6 سال'), (7, '7 تا 12 سال'), (13, 'مناسب برای بالای 13 سال'),
    (17, 'مناسب برای بالای 17 سال'),
)

quality_choice = (
    (1, '1080p'), (2, '720p'),
)


def image_resize(file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    file_path_l = os.path.join(settings.MEDIA_ROOT, 'p/' + file_name)
    img = Image.open(file_path)
    img = img.resize((486, 720))
    img.save(file_path_l)
    img = img.resize((175, 259))
    img.save(file_path)


def image_delete(playlist):
    try:
        if playlist.thumb_image:
            thumb_image = playlist.thumb_image
            if thumb_image.file:
                if os.path.isfile(thumb_image.path):
                    thumb_image.file.close()
                    try:
                        os.remove(thumb_image.path)
                    except:
                        pass
                    try:
                        os.remove(os.path.join(settings.MEDIA_ROOT, 'p/' + thumb_image.name))
                    except:
                        pass
    except:
        pass


def image_path(instance, file_name):
    try:
        playlist = PlayList.objects.get(pk=instance.pk)
        image_delete(playlist)
    except:
        pass
    base_file_name, file_extension = os.path.splitext(file_name)
    if PlayList.objects.count() == 0:
        image_name = str(random.randrange(1000000, 9999999)) + '-' + str(1)
    else:
        image_name = str(random.randrange(1000000, 9999999)) + '-' + str(PlayList.objects.last().id + 1)
    return '{image_name}{ext}'.format(image_name=image_name, ext=file_extension)


def name_to_url(name):
    name = name.replace(' ', '-')
    name = name.lower()
    return name


def random_string(string_length):
    result = random.randrange(1000000, 9999999)
    return str(result)


class Country(models.Model):
    name = models.CharField(max_length=35, unique=True)
    page_url = models.CharField(max_length=255, null=True, blank=True, help_text='This field is Read Only')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.page_url = 'country' + '/' + name_to_url(self.name) + '/'
        super().save(*args, **kwargs)


class Director(models.Model):
    name = models.CharField(max_length=35, unique=True, verbose_name='نام کارگردان')
    summary = models.TextField(max_length=1024, verbose_name='درباره کارگردان')
    thumb_image = models.ImageField(null=True, blank=True, editable=True, upload_to=image_path,
                                    verbose_name='تصویر کارگردان')
    page_url = models.CharField(max_length=255, null=True, blank=True, help_text='This field is Read Only')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("ViewDirector", kwargs={"pk": self.id, "name": self.name})

    def save(self, *args, **kwargs):
        # super().save(*args, **kwargs)
        self.page_url = 'director' + '/' + str(self.id) + '/' + name_to_url(self.name) + '/'
        super().save(*args, **kwargs)


class Actor(models.Model):
    name = models.CharField(max_length=35, unique=True, verbose_name='نام بازیگر')
    summary = models.TextField(max_length=1024, verbose_name='درباره بازیگر')
    thumb_image = models.ImageField(null=True, blank=True, editable=True, upload_to=image_path,
                                    verbose_name='تصویر بازیگر')
    page_url = models.CharField(max_length=255, null=True, blank=True, help_text='This field is Read Only')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("ViewActor", kwargs={"pk": self.id, "name": self.name})

    def save(self, *args, **kwargs):
        # super().save(*args, **kwargs)
        self.page_url = 'actor' + '/' + str(self.id) + '/' + name_to_url(self.name) + '/'
        super().save(*args, **kwargs)


class Category(models.Model):
    index = models.PositiveSmallIntegerField(default=1)
    name_en = models.CharField(max_length=35, unique=True)
    name_fa = models.CharField(max_length=35)
    image = models.ImageField(null=True, blank=True, editable=True, verbose_name='تصویر دسته بندی')
    page_url = models.CharField(max_length=255, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("ByCategory", kwargs={"name_en": self.name_en})

    def __str__(self):
        return self.name_fa


class PlayList(models.Model):
    type = models.PositiveSmallIntegerField(choices=type_choice, default=1, verbose_name='نوع فیلم')
    category = models.ManyToManyField(Category, related_name='Playlists', verbose_name='دسته بندی و ژانر')
    name_en = models.CharField(max_length=55, unique=True, verbose_name='نام انگلیسی')
    name_fa = models.CharField(max_length=55, unique=True, verbose_name='نام فارسی')
    summary = models.TextField(max_length=1024, verbose_name='خلاصه فیلم')
    imdb_score = models.FloatField(default=0, verbose_name='IMDB امتیاز')
    users_score = models.FloatField(default=0, verbose_name='امتیاز کاربران')
    # seen_number = models.FloatField(default=0, verbose_name='تعداد نفراتی که فیلم را مشاهده کرده اند')
    publish_status = models.CharField(max_length=55, null=True, blank=True)
    is_free = models.BooleanField(default=False, verbose_name='رایگان است')
    visit_times = models.IntegerField(default=0)
    play_times = models.IntegerField(default=0)
    year = models.CharField(max_length=10, verbose_name='سال')
    time = models.CharField(max_length=55, verbose_name='مدت زمان فیلم')
    tv_pg = models.PositiveSmallIntegerField(choices=tv_pg_choice, default=5, verbose_name='درجه بندی سنی')
    actor = models.ManyToManyField(Actor, blank=True, verbose_name='بازیگران')
    director = models.ManyToManyField(Director, blank=True, verbose_name='کارگردان')
    thumb_image = models.ImageField(null=True, blank=True, editable=True, upload_to=image_path,
                                    verbose_name='تصویر انگشتی فیلم')
    image_1920x1080 = models.ImageField(null=True, blank=True, editable=True, upload_to=image_path,
                                        verbose_name='تصویر بنر دسکتاپ فیلم')
    image_600x810 = models.ImageField(null=True, blank=True, editable=True, upload_to=image_path,
                                      verbose_name='تصویر بنر موبایل فیلم')
    country = models.ManyToManyField(Country, verbose_name='کشور')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    users_score_n = models.IntegerField(default=0)
    users_score_p = models.IntegerField(default=0)
    trailer_url = models.CharField(max_length=512, null=True, blank=True, verbose_name='آدرس تریلر')
    page_url = models.CharField(max_length=255, null=True, blank=True, help_text='This field is Read Only')

    def __str__(self):
        return self.name_en + ' | Type: ' + str(self.type) + ' | ID: ' + str(self.id)

    def get_absolute_url(self):
        return reverse("playlist", kwargs={"pk": self.id, "name_en": self.name_en, "name_fa": self.name_fa})

    def save(self, *args, **kwargs):
        old_image_name = self.thumb_image.name
        # super().save(*args, **kwargs)

        if self.type == 1:
            self.page_url = 'movie/' + str(self.id) + '/' + name_to_url(self.name_en) + '/' \
                            + name_to_url(self.name_fa) + '/'
        else:
            self.page_url = 'series/' + str(self.id) + '/' + name_to_url(self.name_en) + '/' \
                            + name_to_url(self.name_fa) + '/'
        if old_image_name != self.thumb_image.name:
            image_resize(self.thumb_image.name)
        super().save(*args, **kwargs)

class Season(models.Model):
    name = models.PositiveSmallIntegerField(default=0, choices=season_choice, verbose_name='نام/شماره فصل')
    playlist = models.ForeignKey(PlayList, on_delete=models.CASCADE, related_name='Seasons', verbose_name='فیلم/سریال')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name) + ' - ' + " | Pl : " + self.playlist.name_en


class Episode(models.Model):
    playlist = models.ForeignKey(PlayList, on_delete=models.CASCADE, related_name='Episodes', verbose_name='فیلم/سریال')
    title = models.CharField(max_length=55, blank=True, null=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True, related_name='Episodes'
                               , verbose_name='فصل')
    index = models.PositiveSmallIntegerField(default=1, verbose_name='اپیزود')
    summary = models.TextField(max_length=512, null=True, blank=True, verbose_name='خلاصه این اپیزود')
    thumb_image = models.ImageField(null=True, blank=True, verbose_name='تصویر انگشتی')
    stream_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='لینک پخش ')
    download_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='لینک دانلود')
    subtitle_vtt_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='زیرنویس VTT')
    subtitle_srt_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='زیرنویس SRT')
    page_url = models.CharField(max_length=255, null=True, blank=True, help_text='This field is Read Only')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("episode", kwargs={"pk": self.id})

    def __str__(self):
        return self.playlist.name_en + " | SE: " + str(self.season.name) + ' | Index: ' + str(
            self.index) + ' | ID: ' + str(
            self.id)

    def save(self, *args, **kwargs):
        # super().save()

        self.playlist.updated_at = datetime.now()
        self.playlist.save()

        if self.season is None:
            self.page_url = 'p/' + str(self.id) + '/'
        else:
            self.page_url = 'p/' + str(self.id) + '/'

        super().save(*args, **kwargs)


class Contact(models.Model):
    name = models.CharField(max_length=80)
    mobile_or_email = models.CharField(max_length=80)
    message = models.TextField(max_length=512)

    def __str__(self):
        return self.name + ' - ' + self.message
