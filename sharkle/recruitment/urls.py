from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *
from circle.views import *


app_name = 'recruitment'

router = SimpleRouter()
router.register(r'circle/(?P<circle_id>\d+)/recruitment', RecruitmentViewSet, basename='recruitment')

urlpatterns = [
    path('', include(router.urls))
]