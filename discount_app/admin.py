from django.contrib import admin

# Register your models here.
from discount_app.models import Discount, CheckUserDiscount


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percent', 'jvalid_from', 'jvalid_to', 'active',)
    list_editable = ('active',)
    search_fields = ('title', 'code',)
    list_filter = ('discount_percent', 'active',)


admin.site.register(Discount, DiscountAdmin)


class CheckUserDiscountAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_discount_percent', 'status', 'jdate_use', ]
    list_editable = ('status',)
    list_filter = ('status', "discount__discount_percent")
    readonly_fields = ['jdate_use', ]


admin.site.register(CheckUserDiscount, CheckUserDiscountAdmin)
