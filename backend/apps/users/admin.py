from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.timezone import localtime

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['avatar_icon', 'id', 'telegram_id', 'referrer', 'nickname', 'username', 'phone', 'knockouts', 'rating', 'formatted_created_at']
    list_display_links = ['avatar_icon', 'id', 'telegram_id']
    list_filter = ['is_superuser', 'created_at']
    list_editable = ['knockouts', 'rating']
    search_fields = ['id', 'telegram_id', 'nickname', 'username']
    ordering = ['-created_at']

    fieldsets = (
        ('Идентификатор', {'fields': ('id', 'telegram_id')}),
        ('Персональная информация', {'fields': ('referrer', 'username', 'nickname', 'phone', 'avatar_preview')}),
        ('Игровая статистика', {'fields': ('knockouts', 'rating')}),
        ('Важные даты', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    readonly_fields = ['id', 'telegram_id', 'referrer', 'created_at', 'updated_at', 'last_login', 'avatar_preview']

    def formatted_created_at(self, obj):
        return localtime(obj.created_at).strftime("%d.%m.%Y %H:%M")
    formatted_created_at.short_description = "Created at"
    formatted_created_at.admin_order_field = "created_at"

    def avatar_icon(self, obj):
        if obj.avatar_path:
            return format_html(
                '<img src="{}" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" title="{}" />',
                obj.avatar_path.url, obj.first_name
            )
        return format_html(
            '<div style="width: 24px; height: 24px; border-radius: 50%; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 12px;" title="Нет фото">👤</div>'
        )

    def avatar_preview(self, obj):
        if obj.avatar_path:
            return format_html(
                '''
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img src="{}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid #e0e0e0;" />
                </div>
                ''',
                obj.avatar_path.url
            )
        return format_html('<span style="color: #999;">— Нет фото —</span>')

    avatar_icon.short_description = ""
    avatar_preview.short_description = "Фото профиля"

    def has_add_permission(self, request):
        return False
