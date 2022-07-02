from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *
from circle.views import *


app_name = 'schedule'

router = SimpleRouter()
router.register(r'circle/(?P<circle_id>\d+)/schedule', ScheduleViewSet, basename='recruitment')

urlpatterns = [
    path('', include(router.urls))
]