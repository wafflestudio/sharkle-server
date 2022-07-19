from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *

app_name = "circle"

intro_detail = IntroViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
    }
)
router = SimpleRouter()
router.register("homepage", HomepageViewSet, basename="homepage")  # /circle/
router.register("circle", CircleViewSet, basename="circle")
router.register(
    "circle/(?P<circle_id>\d+)/account", UserCircleViewSet, basename="user_circle_view"
)
router.register(
    "circle/(?P<circle_id>\d+)/account/(?P<user_id>[-\w]+)",
    UserCircleUpdateSet,
    basename="user_circle_update",
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "circle/<int:circle_id>/intro",
        intro_detail,
        name="intro_detail",
    ),
    path(
        "circle/<str:circle_name>/name/", CircleNameView.as_view(), name="circle_name"
    ),
]
