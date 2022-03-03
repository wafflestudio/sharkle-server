from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *


app_name = 'circle'

router = SimpleRouter()
router.register('homepage', HomepageViewSet, basename='homepage')  # /circle/
router.register('circle', CircleViewSet, basename='circle')
router.register('circle/(?P<circle_id>\d+)/account/(?P<user_id>[-\w]+)', UserCircleViewSet, basename='user_circle')

urlpatterns = [
    path('', include(router.urls))
]