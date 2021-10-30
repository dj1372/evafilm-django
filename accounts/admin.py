from django.contrib import admin
from .models import UserProfile, SubscriptionPlan, Subscription


class SubscriptionPlanAdmin(admin.ModelAdmin):
    readonly_fields = ["spacial_id", ]


admin.site.register(UserProfile)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Subscription)
