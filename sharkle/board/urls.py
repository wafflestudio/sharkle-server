from django.urls import include, path
from rest_framework.routers import SimpleRouter
from board.views import BoardViesSet

app_name = "survey"

router = SimpleRouter()
router.register(r"/circle/(?P<circle_id)d+/board/", BoardViesSet, basename="survey")

urlpatterns = [
    path("", include((router.urls))),
]
