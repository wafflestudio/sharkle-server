from django.contrib import admin
from comment.models import Comment

# Register your models here.
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "article",
        "author",
        "content",
        "reply_to",
        "created_at",
        "is_deleted",
    ]
    list_display_links = list_display
    search_fields = list_display


admin.site.register(Comment, CommentAdmin)
# Register your models here.
