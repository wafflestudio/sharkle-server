from django.contrib import admin
from hashtag.models import Hashtag, HashtagCircle

# Register your models here.
class HashtagAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    list_display_links = list_display
    search_fields = list_display


class HashtagCircleAdmin(admin.ModelAdmin):
    list_display = ["id", "hashtag", "circle"]
    list_display_links = list_display
    search_fields = list_display


admin.site.register(Hashtag, HashtagAdmin)
admin.site.register(HashtagCircle, HashtagCircleAdmin)
