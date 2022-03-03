from django.urls import path, include

from user.views import PingPongView, SignUpView, TokenObtainPairView

urlpatterns = [
    path("ping/", PingPongView.as_view(), name="ping"),  # /api/v1/ping/
    path("signup/", SignUpView.as_view(), name="signup"),  # /api/v1/signup/
    path("login/", TokenObtainPairView.as_view(), name="login"),  # /api/v1/login/
]
