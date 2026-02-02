from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from django.utils import timezone

from .models import Tournament, TournamentFeature, TournamentRegistration

class TournamentFeatureForm(forms.ModelForm):
    class Meta:
        model = TournamentFeature
        fields = '__all__'
        widgets = {
            'text': forms.TextInput(attrs={
                'maxlength': '256',
                'placeholder': 'Введите особенность (макс. 256 символов)'
            })
        }
    
    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if len(text) > 256:
            raise forms.ValidationError("Максимальная длина 256 символов")
        if not text:
            raise forms.ValidationError("Это поле обязательно для заполнения")
        return text

class TournamentFeatureInline(admin.TabularInline):
    model = TournamentFeature
    form = TournamentFeatureForm
    extra = 1  # Количество пустых строк по умолчанию
    ordering = ('sort_order',)

    # Настройки внешнего вида
    # classes = ('collapse',)  # Можно свернуть
    min_num = 0  # Минимальное количество особенностей
    # max_num = 10  # Максимальное количество особенностей

    # Кастомизация отображения
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('sort_order')


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    inlines = [TournamentFeatureInline]

    list_display = ['id', 'title', 'location', 'started_at_compact', 'status_badge', 'participants_count', 'tournament_action_button']
    list_display_links = ['id', 'title']
    list_filter = ['status']
    search_fields = ['title', 'location']
    ordering = ['-started_at']

    class Media:
        css = {
            'all': ('admin/tournament.css',)
        }

    def get_fieldsets(self, request, obj=None):
        """Динамические fieldsets в зависимости от создания/редактирования"""
        if obj:  # Редактирование существующего турнира
            return (
                ('Основная информация', {
                    'fields': ('title', 'location', 'started_at', 'general_rules', 'icon')
                }),
                ('Статус', {
                    'fields': ('status_display',)
                }),
                ('Даты', {
                    'fields': ('created_at', 'updated_at')
                }),
                ('Участники', {
                    'fields': ('participants_count_display',)
                }),
            )
        return (
            ('Основная информация', {
                'fields': ('title', 'location', 'started_at', 'general_rules')
            }),
        )

    def participants_count(self, obj):
        return obj.get_participants_count()
    participants_count.short_description = 'Участники'

    def participants_count_display(self, obj):
        count = obj.get_participants_count()
        return format_html('<strong>{}</strong> участника(-ов)', count)
    participants_count_display.short_description = 'Зарегистрировано участников'

    def get_readonly_fields(self, request, obj=None):
        """Динамические readonly поля"""
        if not obj:
            return []

        readonly_fields = ['created_at', 'updated_at', 'status_display', 'participants_count_display']

        if obj.status == 'INACTIVE':
            all_fields = [f.name for f in self.model._meta.fields]
            readonly_fields = all_fields + ['status_display', 'participants_count_display']

        return readonly_fields

    def get_exclude(self, request, obj=None):
        """Динамическое исключение полей"""
        if not obj:  # При создании скрываем статус
            return ['status']
        return []

    # Компактное отображение даты старта
    def started_at_compact(self, obj):
        # return obj.started_at.strftime('%d.%m.%Y %H:%M')
        return timezone.localtime(obj.started_at).strftime('%d.%m.%Y %H:%M')
    started_at_compact.short_description = 'Старт'
    started_at_compact.admin_order_field = 'started_at'

    def status_display(self, obj):
        return self.status_badge(obj)
    status_display.short_description = 'Текущий статус'

    def tournament_action_button(self, obj):
        if obj.status == 'IN_QUEUE':
            return format_html(
                '<a class="button" href="start_tournament/{}/" style="background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">Запустить турнир</a>',
                obj.id
            )
        elif obj.status == 'ACTIVE':
            return format_html(
                '<a class="button" href="finish_tournament/{}/" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">Завершить турнир</a>',
                obj.id
            )
        # Для INACTIVE ничего не отображаем
        return ""
    tournament_action_button.short_description = 'Действие'

    # Красивое отображение статуса
    def status_badge(self, obj):
        status_config = {
            'IN_QUEUE': ('🟡', 'yellow', 'В очереди'),
            'ACTIVE': ('🟢', 'green', 'Активный'),
            'INACTIVE': ('⚫', 'gray', 'Завершен')
        }
        emoji, color, text = status_config.get(obj.status, ('⚫', 'gray', obj.status))
        return format_html(
            '{} <span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">{}</span>',
            emoji, color, text
        )
    status_badge.short_description = 'Статус'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'start_tournament/<int:tournament_id>/', 
                self.admin_site.admin_view(self.start_tournament),
                name='start_tournament'
            ),
            path(
                'finish_tournament/<int:tournament_id>/', 
                self.admin_site.admin_view(self.finish_tournament),
                name='finish_tournament'
            ),
        ]
        return custom_urls + urls

    def start_tournament(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            tournament.started_at = timezone.now()
            tournament.status = 'ACTIVE'
            tournament.save()
            
            self.message_user(
                request, 
                f'Турнир "{tournament.title}" успешно запущен', 
                messages.SUCCESS
            )
        except Tournament.DoesNotExist:
            self.message_user(request, 'Турнир не найден', messages.ERROR)
        
        return redirect('admin:tournaments_tournament_changelist')

    def finish_tournament(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            tournament.status = 'INACTIVE'
            tournament.save()

            self.message_user(
                request, 
                f'Турнир "{tournament.title}" успешно завершен', 
                messages.SUCCESS
            )
        except Tournament.DoesNotExist:
            self.message_user(request, 'Турнир не найден', messages.ERROR)
        
        return redirect('admin:tournaments_tournament_changelist')

    # Показываем предупреждение при редактировании завершенного турнира
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if object_id:
            try:
                obj = Tournament.objects.get(id=object_id)
                if obj.status == 'INACTIVE':
                    extra_context = extra_context or {}
                    extra_context['readonly_message'] = 'Этот турнир завершен и не может быть изменен.'
            except Tournament.DoesNotExist:
                pass
        
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(TournamentRegistration)
class TournamentRegistrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'tournament', 'user', 'status_badge', 'table_number', 'created_at_compact']
    list_filter = ['status', 'tournament', 'created_at']
    search_fields = ['user__username', 'user__nickname', 'tournament__title']
    readonly_fields = ['created_at', 'updated_at']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "tournament":
            # Фильтруем только турниры в очереди
            kwargs["queryset"] = Tournament.objects.filter(status=Tournament.StatusType.IN_QUEUE)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def status_badge(self, obj):
        status_config = {
            'REGISTERED': ('🟢', 'green', 'Зарегистрирован'),
            'WAITLIST': ('🟡', 'yellow', 'В листе ожидания'),
            'CANCELLED': ('🔴', 'red', 'Отменена'),
        }
        emoji, color, text = status_config.get(obj.status, ('⚫', 'gray', obj.status))
        return format_html(
            '{} <span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">{}</span>',
            emoji, color, text
        )
    status_badge.short_description = 'Статус'

    def created_at_compact(self, obj):
        # return obj.created_at.strftime('%d.%m.%Y %H:%M')
        return timezone.localtime(obj.created_at).strftime('%d.%m.%Y %H:%M')
    created_at_compact.short_description = 'Зарегистрирован'