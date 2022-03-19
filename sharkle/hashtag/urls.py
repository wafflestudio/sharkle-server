from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *


app_name = "hashtag"

router = SimpleRouter()
router.register("hashtag", HashTagViewSet, basename="hashtag")  # /circle/

urlpatterns = [path("", include(router.urls))]
