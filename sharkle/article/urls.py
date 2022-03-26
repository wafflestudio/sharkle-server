from django.urls import include, path
from rest_framework.routers import SimpleRouter
from article.views import ArticleViewSet

app_name = "article"

router = SimpleRouter()
router.register(
    r"circle/(?P<circle_id>\d+)/board/(?P<board_id>\d+)/article",
    ArticleViewSet,
    basename="article",
)

urlpatterns = [
    path("", include(router.urls)),
]
