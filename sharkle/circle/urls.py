from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *


app_name = 'circle'

router = SimpleRouter()
router.register('homepage', HomepageViewSet, basename='homepage')  # /circle/
router.register('circle', CircleViewSet, basename='circle')


urlpatterns = [
    path('', include(router.urls))
]