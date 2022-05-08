from django.urls import include, path
from rest_framework.routers import SimpleRouter
from board.views import *

app_name = "board"

router = SimpleRouter()
router.register(r"circle/(?P<circle_id>\d+)/board", BoardViewSet, basename="board")

urlpatterns = [
    path("", include(router.urls)),
    path("circle/<str:circle_name>/board/", get_board_list_by_circle_name),
]
