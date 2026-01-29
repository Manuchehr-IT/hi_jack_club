from django.contrib import admin
from django.utils.html import format_html
from .models import SocialNetwork

@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    list_display = ('social_type', 'url_preview', 'updated_at')
    # list_editable = ('is_active',)
    readonly_fields = ('social_type', 'updated_at')

    # Показываем только существующие типы, нельзя добавить новые
    def has_add_permission(self, request):
        count = SocialNetwork.objects.count()
        return count < 6

    def has_delete_permission(self, request, obj=None):
        return False  # ← Запрещаем удаление

    # 3. Запретить массовое удаление (действие "delete selected")
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def url_preview(self, obj):
        if obj.url:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                obj.url,
                obj.url[:50] + '...' if len(obj.url) > 50 else obj.url
            )
        return '-'
    url_preview.short_description = 'Ссылка'

    # Простые поля для редактирования
    fields = ('social_type', 'url', 'updated_at')
