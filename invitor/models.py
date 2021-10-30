from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from django.contrib.auth import get_user_model

User = get_user_model()


class invitor_code(models.Model):
    class Meta:
        verbose_name = "کد معرف"
        verbose_name_plural = "کدهای معرف"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='myuser')
    code = models.CharField(max_length=11)
    invitations = models.IntegerField(blank=True, null=True)
    invited_users = models.ManyToManyField(User, related_name='invited_users', blank=True)

    def save(self, *args, **kwargs):
        if not self.invitations:
            self.invitations=0
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.code


class generated_invitor_code(models.Model):
    class Meta:
        verbose_name = "کد معرف دستی"
        verbose_name_plural = "کدهای معرف دستی"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_g', blank=True, null=True)
    code = models.CharField(max_length=30)
    invitations = models.IntegerField(blank=True, null=True)
    invited_users = models.ManyToManyField(User, related_name='invited_users_g', blank=True)

    def save(self, *args, **kwargs):
        if not self.invitations:
            self.invitations = 0
        if not self.code:
            self.code = self.pk*11+12345
        if not self.user:
            self.user = User.objects.get(username="admin")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.code


