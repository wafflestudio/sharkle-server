from django.urls import path, include

from user.views import PingPongView, SignUpView, TokenObtainPairView
from user.send_email import EmailSendView

urlpatterns = [
    path("ping/", PingPongView.as_view(), name="ping"),  # /api/v1/ping/
    path("auth/signup/", SignUpView.as_view(), name="signup"),  # /api/v1/auth/signup/
    path(
        "auth/login/", TokenObtainPairView.as_view(), name="login"
    ),  # /api/v1/auth/login/
    path(
        "auth/email/send/", EmailSendView.as_view(), name="send_email"
    ),  # /api/v1/auth/signup/
]
