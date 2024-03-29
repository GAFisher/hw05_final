from django.conf import settings
from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "text",
        "pub_date",
        "author",
        "group",
    )
    list_editable = ("group",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "slug",
        "description",
    )
    list_editable = ("slug",)
    search_fields = ("title",)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
