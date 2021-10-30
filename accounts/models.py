from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from movies.models import PlayList, Category, Episode
import random
from datetime import datetime
from datetime import timedelta
import uuid

from invitor.models import invitor_code, generated_invitor_code

from django.contrib.auth import get_user_model

User = get_user_model()


class SubscriptionPlanManager(models.Manager):
    def get_object_or_none(self, plan_name):
        try:
            selected_plan = self.get_queryset().get(name=plan_name)
        except:
            return None
        return selected_plan

    def get_object_or_none_sp(self, spacial_id):
        try:
            selected_plan = self.get_queryset().get(spacial_id=spacial_id)
        except:
            return None
        return selected_plan


def generate_random_uuid():
    return str(uuid.uuid4())[:8]


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=5)
    title = models.CharField(max_length=55)
    valid_days = models.PositiveSmallIntegerField()
    price = models.IntegerField()
    is_vip = models.BooleanField(default=False)
    # ------------------- my field ------------------------
    spacial_id = models.CharField(max_length=8, default=generate_random_uuid)
    max_valid_days = models.PositiveSmallIntegerField(default=120)

    objects = SubscriptionPlanManager()

    def __str__(self):
        return self.name + ' - ' + self.title

    class Meta:
        verbose_name = "مدیریت نوع اشتراک"
        verbose_name_plural = "مدیریت نوع اشتراک"


class SubscriptionManager(models.Manager):
    def get_user_plan(self, user, plan):
        try:
            user_plan = self.get_queryset().get(user=user)
        except:
            return None
        return user_plan

    def get_older_or_none(self, plan_name, end_date):
        try:
            selected_plan = self.get_queryset().get(name=plan_name, end_date=end_date)
        except:
            return None
        return selected_plan


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='SubscriptionPlan')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    ip_1 = models.CharField(max_length=15, null=True, blank=True)
    ip_2 = models.CharField(max_length=15, null=True, blank=True)
    ip_3 = models.CharField(max_length=15, null=True, blank=True)

    objects = SubscriptionManager()

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.start_date = datetime.now().date()
        self.start_time = datetime.now().time()
        #     self.end_date = datetime.now().date() + timedelta(self.plan.valid_days)
        self.end_time = datetime.now().time()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "مدیریت اشتراک کاربران"
        verbose_name_plural = "مدیریت اشتراک کاربران"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='Profile')
    nick_name = models.CharField(max_length=12, null=True, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True, default=28)
    is_verified = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    api_token = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateField()
    last_login = models.DateField(null=True, blank=True)
    is_censor_on = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    def save(self, *arg, **kwargs):
        self.created_at = datetime.now().date()
        if self.nick_name is None:
            self.nick_name = 'U' + str(self.user.id + random.randrange(528890, 998890))
        super().save(*arg, **kwargs)

    class Meta:
        verbose_name = "حساب کاربری"
        verbose_name_plural = "حساب کاربری"


@receiver(post_save, sender=UserProfile)
def invitor_code_creator(instance, **kwargs):
    if not invitor_code.objects.filter(user=instance.user).exists():
        invitor_code.objects.create(user=instance.user, code=instance.user.username, invitations=0)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        if not User.is_staff:
            sub = Subscription.objects.create(user=instance)
            sub.plan = SubscriptionPlan.objects.get(name='P10')
            sub.start_date = datetime.now().date()
            sub.start_time = datetime.now().time()
            sub.end_date = datetime.today().date() + timedelta(days=sub.plan.valid_days)
            sub.end_time = datetime.now().time()
            sub.save()
