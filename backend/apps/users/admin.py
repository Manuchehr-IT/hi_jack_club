import csv

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.timezone import localtime

from .models import UserRewardLog

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['avatar_icon', 'id', 'telegram_id', 'referrer', 'nickname', 'username', 'phone', 'knockouts', 'points', 'formatted_created_at']
    list_display_links = ['avatar_icon', 'id', 'telegram_id']
    list_filter = ['is_superuser', 'created_at']
    list_editable = ['knockouts', 'points']
    search_fields = ['id', 'telegram_id', 'nickname', 'username', 'phone']
    ordering = ['-created_at']
    actions = ['export_as_csv']

    fieldsets = (
        ('Идентификатор', {'fields': ('id', 'telegram_id')}),
        ('Персональная информация', {'fields': ('referrer', 'username', 'nickname', 'phone', 'avatar_preview')}),
        ('Игровая статистика', {'fields': ('knockouts', 'points')}),
        ('Важные даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ['id', 'telegram_id', 'username', 'nickname', 'phone', 'referrer', 'created_at', 'updated_at', 'avatar_preview']

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=users.csv'

        writer = csv.writer(response)
        # Заголовки
        writer.writerow(['ID', "Telegram ID", "Referrer ID", 'Nickname', 'Username', 'First name', 'Phone', 'Knockouts', 'Points', 'Created At'])

        # Данные
        for user in queryset:
            writer.writerow([
                user.id,
                user.telegram_id,
                user.referrer.id if user.referrer else None,
                user.nickname,
                user.username,
                user.first_name,
                user.phone,
                user.knockouts,
                user.points,
                localtime(user.created_at).strftime("%d.%m.%Y %H:%M")
            ])

        return response

    export_as_csv.short_description = "Экспорт выбранных пользователей в CSV"

    def formatted_created_at(self, obj):
        return localtime(obj.created_at).strftime("%d.%m.%Y %H:%M")
    formatted_created_at.short_description = "Created at"
    formatted_created_at.admin_order_field = "created_at"

    @admin.display(description="")
    def avatar_icon(self, obj):
        if obj.avatar_path:
            return format_html(
                '<img src="{}" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" title="{}" />',
                obj.avatar_path.url, obj.first_name
            )
        return format_html(
            '<div style="width: 24px; height: 24px; border-radius: 50%; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 12px;" title="Нет фото">👤</div>'
        )

    @admin.display(description="Фото профиля")
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

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(UserRewardLog)
class UserRewardLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'operation', 'reward', 'count', 'comment', 'created_at']
    list_filter = ['user', 'operation', 'reward', 'created_at']
    search_fields = ['user', 'comment']
    ordering = ['-created_at']

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
