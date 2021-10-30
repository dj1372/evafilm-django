from django.utils import timezone
from datetime import datetime, timedelta
from django.db import models
import uuid
from django.contrib.auth import get_user_model
from extensions.utils import jalali_converter
from movies.models import Category

User = get_user_model()


def generate_random_code():
    return str(uuid.uuid4())[:8]


class GiftCardManager(models.Manager):
    def get_object_or_None(self, code, now):
        try:
            obj = self.get_queryset().get(code=code, valid_from__lt=now, valid_to__gt=now, active=True)
        except:
            return None
        return obj


class GiftCard(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان", default="")
    code = models.CharField(default=generate_random_code(), verbose_name="کد کارت هدیه", max_length=255, unique=True)
    category = models.ManyToManyField(
        Category, verbose_name="دسته ها", related_name="category")
    valid_from = models.DateTimeField(verbose_name='فعال از',
                                      help_text=("در این فیلد تعیین کنید از چه زمانی کارت هدیه فعال باشد",))
    valid_to = models.DateTimeField(verbose_name='زمان پایان',
                                    help_text=("در  این فیلد تعریف کنید کارت هدیه تا چه زمانی فعال باشد",))
    valid_day = models.IntegerField(verbose_name='مدت اعتبار',
                                    help_text=("در  این فیلد تعریف کنید کارت هدیه تا چند روز اعتبار دارد",))
    active = models.BooleanField(verbose_name="وضعیت", default=False)

    objects = GiftCardManager()

    def save(self, *arg, **kwargs):
        end_time = self.valid_to
        now = timezone.now()
        if now > end_time:
            self.active = False
        super().save(*arg, **kwargs)

    class Meta:
        verbose_name = "کارت هدیه"
        verbose_name_plural = "کارت های هدیه"

    def __str__(self):
        return f"{self.title}"

    def jvalid_from(self):
        return jalali_converter(self.valid_from)

    jvalid_from.short_description = "فعال از"

    def jvalid_to(self):
        return jalali_converter(self.valid_to)

    jvalid_to.short_description = "فعال تا"

    def jvalid_day(self):
        return f"{self.valid_day} روز "

    jvalid_day.short_description = "زمان استفاده"


class GiftCard_Related_to_User_Manager(models.Manager):
    def get_object_or_None_for_check_use(self, gift_code, user):
        try:
            gift = self.get_queryset().get(gift_code=gift_code, user=user)
        except:
            return None
        return gift

    def get_object_or_None_for_check_cat(self, user, status):
        try:
            gift = self.get_queryset().get(user=user, status=status)
        except:
            return None
        return gift


class GiftCard_Related_to_User(models.Model):
    gift_code = models.OneToOneField(GiftCard, on_delete=models.CASCADE, related_name="giftcard")
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="کاربر", related_name="user")
    date_enabeld = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=True, verbose_name="وضعیت استفاده")

    class Meta:
        verbose_name = "وضعیت کارت هدیه"
        verbose_name_plural = "وضعیت کارت های هدیه"

    objects = GiftCard_Related_to_User_Manager()

    def __str__(self):
        return f"{self.user.username}_{self.gift_code.title}"

    def jdate_enabeld(self):
        return jalali_converter(self.date_enabeld)

    jdate_enabeld.short_description = "روز فعال شذه"
