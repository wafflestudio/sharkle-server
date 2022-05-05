from django.contrib import admin
from circle.models import Circle

# Register your models here.
class CircleAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "tag"]


admin.site.register(Circle, CircleAdmin)
