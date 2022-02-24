from django.urls import path, include

from user.views import PingPongView

urlpatterns = [
    path('ping/', PingPongView.as_view(), name='ping'),  # /api/v1/ping/
]