from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserViewSet

from user.send_email import EmailViewSet
from user.views import PingPongView, SignUpView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = SimpleRouter()
router.register("email", EmailViewSet, basename="email")  # /api/v1/email/
router.register("account", UserViewSet, basename="happyUser")  # /account/

urlpatterns = [
    path("ping/", PingPongView.as_view(), name="ping"),  # /api/v1/ping/
    path("auth/signup/", SignUpView.as_view(), name="signup"),  # /api/v1/auth/signup/
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),  # /api/v1/auth/login/
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="refresh"),  # /api/v1/auth/token/refresh/
    path("auth/token/verify/", TokenVerifyView.as_view(), name="verify"),  # /api/v1/auth/token/verify/
    path("", include(router.urls)),
]
