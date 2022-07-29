from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import UserBoardAlarmViewSet, UserCircleViewSet

app_name = "user_circle"

router = SimpleRouter()
router.register("circle/(?P<circle_id>\d+)/user", UserCircleViewSet, basename="user_circle_view")
router.register("circle/(?P<circle_id>\d+)/user/(?P<user_id>[-\w]+)", UserBoardAlarmViewSet,basename="user_board_alarm")

urlpatterns = [
    path("", include(router.urls)),
]
