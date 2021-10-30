from django.db import models
import uuid
from django.contrib.auth import get_user_model
from extensions.utils import jalali_converter

User = get_user_model()


def generate_random_code():
    return str(uuid.uuid4())[:19:-1]


class DiscountManager(models.Manager):

    def get_object_or_None(self, code, now):
        try:
            discount = self.get_queryset().get(code=code, valid_from__lt=now, valid_to__gt=now, active=True)
        except:
            return None
        return discount

    def get_object_or_None_v2(self, code):
        try:
            discount = self.get_queryset().get(code=code, active=True)
        except:
            return None
        return discount


class Discount(models.Model):
    title = models.CharField(max_length=120, default="", blank=False, null=False, verbose_name="عنوان کد تخفیف")
    code = models.CharField(max_length=16, unique=True, verbose_name="کد تخفیف", null=True, blank=True,
                            default=generate_random_code)
    discount_percent = models.IntegerField(verbose_name="در صد کد تخفیف ", default=0)
    valid_from = models.DateTimeField(verbose_name='فعال از', blank=True, null=True,
                                      help_text=("در این فیلد تعیین کنید از چه زمانی کد تخفیف فعال باشد",))
    valid_to = models.DateTimeField(verbose_name='زمان پایان', blank=True, null=True,
                                    help_text=("در  این فیلد تعریف کنید کد تخفیف تا چه زمانی فعال باشد",))
    active = models.BooleanField(verbose_name="وضعیت", default=True)

    objects = DiscountManager()

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کد های تخفیف"

    def __str__(self):
        return f"{self.title}_{self.discount_percent}"

    def jvalid_from(self):
        return jalali_converter(self.valid_from)

    jvalid_from.short_description = "فعال از"

    def jvalid_to(self):
        return jalali_converter(self.valid_to)

    jvalid_to.short_description = "فعال تا"


class CheckUserDiscountManager(models.Manager):
    def get_object_or_None(self, user, code):
        try:
            dis = Discount.objects.get(code=code)
            use_check = self.get_queryset().all().filter(user=user, discount=dis, status=False).first()
        except:
            return None
        return use_check

    def get_object_or_None_w_s(self, user, code):
        try:
            dis = Discount.objects.get(code=code)
            use_check = self.get_queryset().all().filter(user=user, discount=dis).first()
        except:
            return None
        return use_check

    def get_object_status(self, user, code):
        dis = Discount.objects.get(code=code)
        return self.get_queryset().get(user=user, discount=dis)


class CheckUserDiscount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, verbose_name="کد تخفیف", related_name="discount")
    status = models.BooleanField(default=False, blank=True, null=True, verbose_name="استفاده شده یا نه")
    date_use = models.DateTimeField(auto_now_add=True)

    objects = CheckUserDiscountManager()

    class Meta:
        verbose_name = "دسترسی"
        verbose_name_plural = "دسترسی کد های  تخفیف"

    def jdate_use(self):
        return jalali_converter(self.date_use)
    jdate_use.short_description = "زمان استفاده"

    def get_discount_percent(self):
        return F"{self.discount.discount_percent}"
    get_discount_percent.short_description = "درصد تخفیف"
