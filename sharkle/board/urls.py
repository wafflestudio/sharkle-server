from django.urls import include, path
from rest_framework.routers import SimpleRouter
from board.views import BoardViewSet

app_name = "survey"

router = SimpleRouter()
router.register(r"circle/(?P<circle_id>\d+)/board", BoardViewSet, basename="board")

urlpatterns = [
    path("", include(router.urls)),
]