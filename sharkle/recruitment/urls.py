from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import RecruitmentScheduleViewSet, RecruitmentViewSet


app_name = 'recruitment'

router = SimpleRouter()
router.register(r'circle/(?P<circle_id>\d+)/recruitment', RecruitmentViewSet, basename='recruitment')
router.register(r'circle/(?P<circle_id>\d+)/recruitment/(?P<recruitment_id>[-\w]+)/schedule', RecruitmentScheduleViewSet, basename='recruitment_schedule')

urlpatterns = [
    path('', include(router.urls))
]