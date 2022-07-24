from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *


app_name = "media"

router = SimpleRouter()

urlpatterns = [
    path("image/", ImageUploadView.as_view(), name="image"),
    path("", include(router.urls)),
]
