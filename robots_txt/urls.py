from django.urls import path
from robots_txt.views import robots

app_name = "robots_txt"

urlpatterns = [
    path("robots.txt", robots)
]
