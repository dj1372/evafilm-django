from django.contrib import admin
from .models import Episode_Last_State


# Register your models here.
class Admin_Episode_Last_State(admin.ModelAdmin):
    list_display = ("user", "post_id")


admin.site.register(Episode_Last_State, Admin_Episode_Last_State)
