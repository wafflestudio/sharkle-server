from django.contrib import admin
from user.models import User

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email", "user_id"]
    list_display_links = ["id", "username", "email", "user_id"]
    search_fields = ["id", "username", "email", "user_id"]


admin.site.register(User, UserAdmin)
