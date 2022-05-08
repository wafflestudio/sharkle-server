from django.contrib import admin
from recruitment.models import RecruitmentSchedule, Recruitment

# Register your models here.
class RecruitmentAdmin(admin.ModelAdmin):
    list_display = ["id", "circle", "introduction"]
    list_display_links = list_display
    search_fields = list_display


class RecruitmentScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "due"]
    list_display_links = list_display
    search_fields = list_display

    def due(self, schedule):
        return f"{schedule.start} ~ {schedule.end or '~~~'}"


admin.site.register(RecruitmentSchedule, RecruitmentScheduleAdmin)
