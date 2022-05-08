from django.contrib import admin
from board.models import Board

# Register your models here.
class BoardAdmin(admin.ModelAdmin):
    list_display = ["id", "circle", "name", "created_at", "is_private"]
    list_display_links = list_display
    search_fields = list_display


admin.site.register(Board, BoardAdmin)
