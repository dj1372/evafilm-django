from django.db import models


class Robots(models.Model):
    SELECT_TYPE_CHOICES = (("Allow", "مجاز"), ("Disallow", "غیر مجاز"))
    select_type = models.CharField(max_length=8, verbose_name="نوع", choices=SELECT_TYPE_CHOICES, default="Allow")
    value = models.CharField(verbose_name="مقدار", max_length=255, default="")

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "روبات"
