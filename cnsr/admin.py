from django.contrib import admin

from cnsr.models import StartAppCnsr, MiddelAppCnsr, EndAppCnsr


class StartAppCnsrAdmin(admin.ModelAdmin):
    list_display = ["__str__", "e", "active"]
    list_filter = ['active', ]
    search_fields = ["episode__title"]
    readonly_fields = ("s",)


class MiddelAppCnsrAdmin(admin.ModelAdmin):
    list_display = ["__str__", "s", "e", "active"]
    list_filter = ['active', ]
    search_fields = ["episode__title"]


class EndAppCnsrAdmin(admin.ModelAdmin):
    list_display = ["__str__", "s", "e", "active"]
    list_filter = ['active', ]
    search_fields = ["episode__title"]


admin.site.register(StartAppCnsr, StartAppCnsrAdmin)
admin.site.register(MiddelAppCnsr, MiddelAppCnsrAdmin)
admin.site.register(EndAppCnsr, EndAppCnsrAdmin)
