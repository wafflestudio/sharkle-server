from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *


app_name = 'circle'

router = SimpleRouter()
router.register('circle', CircleViewSet, basename='circle')  # /circle/


urlpatterns = [
    path('', include(router.urls))
]