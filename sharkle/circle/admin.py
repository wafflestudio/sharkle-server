from django.contrib import admin
from circle.models import Circle

# Register your models here.
class CircleAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "tag"]
    list_display_links = list_display
    search_fields = list_display


admin.site.register(Circle, CircleAdmin)
