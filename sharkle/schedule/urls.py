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

# 선형대수학
# 통계학과, 수학
# 해석개론