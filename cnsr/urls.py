from django.urls import path, include
from rest_framework import routers
from cnsr.views import StartAppCnsrView, MiddelAppCnsrView, EndAppCnsrView, ListS

app_name = "cnsr_api"

router = routers.DefaultRouter()

router.register("SACV", StartAppCnsrView)
router.register("MACV", MiddelAppCnsrView)
router.register("EACV", EndAppCnsrView)

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/li/<int:episode>/", ListS.as_view()),
]
