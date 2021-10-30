from django.db import models
from django.utils import timezone

from extensions.utils import jalali_converter

from django.contrib.auth import get_user_model

User = get_user_model()


class Send_Message(models.Model):
	title = models.CharField(max_length=200, verbose_name="عنوان ارسالی")
	SELECT_CHOICES = (
        ("e", "ارسال ایمیل"),
        ("p", "ارسال پیامک"),
        ("b", "ارسال هردو"),)
	select = models.CharField(
    	max_length=1, choices=SELECT_CHOICES, verbose_name="نحوه ارسال")
	users = models.ManyToManyField(User, verbose_name="اعضای را انتخاب کنید", blank=False,related_name="all_user")
	message = models.TextField(verbose_name="پیام شما", blank=False, null=False)

	publish = models.DateTimeField(
        auto_now_add=timezone.now, verbose_name= "زمان انتشار")

	STATUS_CHOICES = (
        ("d", "منتظر ارسال"),
        ("p", "ارسال"),
    )
	status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, verbose_name="زمان ارسال", blank=True, null=True)
	active = models.BooleanField(verbose_name="وضعیت پیام", default=True)
    
	def __str__(self):
		return self.title

	def get_all_user(self):
		return self.users.filter(is_active=True)

	def jpublish(self):
		return jalali_converter(self.publish)
	jpublish.short_description = "زمان انتشار"


	class Meta:
		verbose_name = "ارسال"
		verbose_name_plural = "ارسالی به کاربران"