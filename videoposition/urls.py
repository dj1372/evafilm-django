# from .views import get_last_position,create_last_position,set_last_position
from django.urls import path
from .views import get_last_position, set_last_position

urlpatterns = [
    path("get_last_position/", get_last_position),
    path("set_last_position/", set_last_position),

]
