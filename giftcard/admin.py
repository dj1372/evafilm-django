from datetime import timedelta

from django.utils import timezone

from extensions.utils import jalali_converter
from django.contrib import admin
# Register your models here.
from giftcard.models import GiftCard, GiftCard_Related_to_User


class GiftCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'jvalid_from', 'jvalid_to', 'valid_day', 'active']


class GiftCard_Related_to_UserAdmin(admin.ModelAdmin):
    list_display = ['gift_code', 'user', 'jdate_enabeld', "jleft_over_account", 'status']

    def jleft_over_account(self, obj):
        obj.date_enabeld + timedelta(days=obj.gift_code.valid_day)
        return jalali_converter(timezone.localtime(obj.date_enabeld + timedelta(days=obj.gift_code.valid_day)))

    jleft_over_account.short_description = "زمان پایان"


admin.site.register(GiftCard, GiftCardAdmin)
admin.site.register(GiftCard_Related_to_User, GiftCard_Related_to_UserAdmin)
