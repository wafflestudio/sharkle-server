from django.contrib import admin
from article.models import Article

# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "content", "board", "author", "is_private", "created_at"]
    list_display_links = list_display
    search_fields = list_display


admin.site.register(Article, ArticleAdmin)
