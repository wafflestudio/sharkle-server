from django.contrib import admin
from user.models import User

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email", "user_id"]
    list_display_links = list_display
    search_fields = list_display


admin.site.register(User, UserAdmin)
