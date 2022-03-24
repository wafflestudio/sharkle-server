from django.urls import include, path
from rest_framework.routers import SimpleRouter
from comment.views import CommentViewSet

app_name = "article"

router = SimpleRouter()
router.register(
    r"article/(?P<article_id>\d+)/comment",
    CommentViewSet,
    basename="comment",
)

urlpatterns = [
    path("", include(router.urls)),
]
