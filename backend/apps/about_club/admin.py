# admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import AboutClub, AboutClubImage

class AboutClubImageInline(admin.TabularInline):
    model = AboutClubImage
    extra = 1
    fields = ("image_preview", "image", "alt", "sort_order")
    readonly_fields = ("image_preview",)
    ordering = ("sort_order",)

    class Media:
        js = ("admin/js/about_club.js",)

@admin.register(AboutClub)
class AboutClubAdmin(admin.ModelAdmin):
    list_display = ("id", "sort_order", "is_active", "created_at")
    list_editable = ("sort_order", "is_active")
    ordering = ("sort_order", "id")
    inlines = [AboutClubImageInline]

    fieldsets = (
        (None, {
            "fields": ("sort_order", "is_active")
        }),
        ("Контент", {
            "fields": ("text",)
        }),
        # ("Даты", {
        #     "fields": ("created_at", "updated_at"),
        #     # "classes": ("collapse",)
        # }),
    )

    readonly_fields = ("created_at", "updated_at")

