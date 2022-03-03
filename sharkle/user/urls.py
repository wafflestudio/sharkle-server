from django.urls import path, include

from user.views import PingPongView, SignUpView, TokenObtainPairView

urlpatterns = [
    path("ping/", PingPongView.as_view(), name="ping"),  # /api/v1/ping/
    path("auth/signup/", SignUpView.as_view(), name="signup"),  # /api/v1/auth/signup/
    path(
        "auth/login/", TokenObtainPairView.as_view(), name="login"
    ),  # /api/v1/auth/login/
]
