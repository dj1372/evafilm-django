from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class Episode_Last_State(models.Model):
    post_id = models.IntegerField()
    last_position = models.FloatField(verbose_name="اخرین تایم به ثانیه")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "User: " + self.user.username + "_" + "Episode ID: " + str(self.post_id)

    class Meta():
        verbose_name = 'جزئیات آخرین فیلم-زمان ذخیره شده کاربران'
        verbose_name_plural = 'جزئیات آخرین فیلم-زمان ذخیره شده کاربران'
