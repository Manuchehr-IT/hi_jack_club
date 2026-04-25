import csv
from decimal import Decimal
from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from django.utils import timezone

from .factory import create_tournament_service
from .models import Tournament, TournamentConfig, TournamentRewardDistributionTemplate, TournamentRewardDistribution, TournamentEventLog, TournamentFeature, TournamentRegistration

for model in [User, Group]:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

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
    ordering = ['sort_order']

    classes = ['collapse']
    min_num = 0

    # Кастомизация отображения
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('sort_order')


class TournamentConfigInline(admin.StackedInline):  # или TabularInline
    model = TournamentConfig
    extra = 0

    classes = ['collapse']
    min_num = 1
    max_num = 1
    can_delete = False

    class Media:
        css = {
            'all': ['admin/css/hide-inline-header.css']
        }


class TournamentEventLogFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        user_events = {}
        # count_entry = 0
        # count_elimination = 0

        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                event_type = form.cleaned_data.get("event")
                user = form.cleaned_data.get("user") or form.cleaned_data.get("comment")

                if not user:
                    continue

                if event_type in ["ENTRY", "FREE_ENTRY", "FREE_ENTRY_DEP", "ELIMINATION"]:
                    if user not in user_events:
                        user_events[user] = {"ENTRY": 0, "ELIMINATION": 0}

                    if event_type in ["ENTRY", "FREE_ENTRY", "FREE_ENTRY_DEP"]:
                        user_events[user]["ENTRY"] += 1
                    elif event_type == "ELIMINATION":
                        user_events[user]["ELIMINATION"] += 1

        for user, events in user_events.items():
            count_entry = events["ENTRY"]
            count_elimination = events["ELIMINATION"]

            if user and (count_entry > 1 or count_elimination > 1):
                raise forms.ValidationError(format_html(
                    "У пользователя <b>{}</b> должно быть по 1 Entry и Elimination, сейчас Entry: {}; Elimination: {}",
                    user, count_entry, count_elimination
                ))

            if count_entry != count_elimination:
                if user:
                    raise forms.ValidationError(format_html(
                        "У пользователя <b>{}</b> Отсутвует {}",
                        user, 'Entry' if count_entry == 0 else 'Elimination'
                    ))
                raise forms.ValidationError(f"У неизвестных пользователей неравное кол-во Entry и Elimination")

class TournamentEventLogInline(admin.TabularInline):
    model = TournamentEventLog
    formset = TournamentEventLogFormSet
    extra = 0

    # classes = ["collapse"]
    verbose_name = "Событие"
    verbose_name_plural = "События"

    fields = ['user', 'event', 'count', 'multiplier', 'recorded_at', 'comment']

    class Media:
        css = {
            'all': ['admin/css/hide-inline-original.css']
        }


class TournamentRewardDistributionFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        total = Decimal("0")

        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                percent = form.cleaned_data.get('percent', Decimal("0"))
                total += percent

        if 100 < total > 0:
            raise ValidationError(f'Сумма процентов должна быть 100% или 0%, сейчас: {total}%')

class TournamentRewardDistributionInline(admin.TabularInline):
    model = TournamentRewardDistribution
    formset = TournamentRewardDistributionFormSet
    extra = 0
    min_num = 1

    class Media:
        css = {
            'all': ['admin/css/hide-inline-original.css']
        }

    # def save_model(self, request, obj, form, change):
    #     # Сохраняем template первым, если его еще нет в БД
    #     if obj.template and not obj.template.pk:
    #         obj.template.save()
    #     super().save_model(request, obj, form, change)

@admin.register(TournamentRewardDistributionTemplate)
class TournamentRewardDistributionTemplateAdmin(admin.ModelAdmin):
    inlines = [TournamentRewardDistributionInline]

    list_display = ['id', 'title', 'created_at', 'updated_at']
    search_fields = ['title']
    ordering = ['-created_at']


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    inlines = [TournamentFeatureInline, TournamentConfigInline]

    list_display = ['id', 'title', 'location', 'started_at_compact', 'status_badge', 'participants_count', 'tournament_action_button']
    list_display_links = ['id', 'title']
    list_filter = ['status']
    search_fields = ['title', 'location']
    ordering = ['-started_at']
    actions = ['update_event_logs', 'recalc_event_logs']

    def get_fieldsets(self, request, obj=None):
        fields = [
            ["Основная информация", {
                "fields": ["title", "location", "started_at", "general_rules", "max_participants", "max_waitlist", "icon"]
            }],
            ["Награды", {
                "fields": ["bank_points", "reward_distribution_template"]
            }],
        ]

        if obj:  # Редактирование существующего турнира
            fields.extend([
                ["Статус", {
                    "fields": ["status_display", "olap_report_completed"]
                }],
                ["Даты", {
                    "fields": ["created_at", "updated_at"]
                }],
                ["Участники", {
                    "fields": ["participants_count_display"]
                }],
            ])

        return fields

    def get_inlines(self, request, obj=None):
        if obj and obj.status == Tournament.StatusType.INACTIVE:
            return [*self.inlines, TournamentEventLogInline]

        return self.inlines


    @admin.action(description="Пересчитать журнал событий турнира для рейтинга")
    def recalc_event_logs(self, request, queryset):
        count = 0
        for tournament in queryset:
            tournament.recalc_all_registrations()
            count += 1

        self.message_user(request, f"Пересчитаны рейтинги пользователей в турнирах: {count}")

    @admin.action(description="Обновить журнал событий турнира из OLAP отчёта")
    def update_event_logs(self, request, queryset):
        tournament_service = create_tournament_service()
        count = 0

        for tournament in queryset:
            tournament_service.process_olap_report(tournament.id, is_forced=True)
            count += 1

        self.message_user(request, f"Обновлено {count} турниров")

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
            # tournament.started_at = timezone.now()
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
    list_display = ['id', 'tournament', 'tournament_status', 'user_nickname', 'user_username', 'user_phone', 'knockouts', 'points', 'status_badge', 'created_at_compact']
    exclude = ["attended", "table_number"]
    list_filter = ['status', 'tournament', 'created_at']
    search_fields = ['user__username', 'user__nickname', 'user__phone', 'tournament__title']
    readonly_fields = ["rankings_calculated", "knockouts", "points", 'created_at', 'updated_at']
    # readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['user', 'tournament']
    actions = ["export_as_csv"]

    @admin.action(description="Экспорт выбранных регистраций в CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=users.csv'

        writer = csv.writer(response)
        writer.writerow([
            'ID', "Tournament Title", "Tournament Status", 'Tournament Started At', 'First name', 'Username', 'Nickname', 'Phone', 'Knockouts', 'Points', 'Created at'
        ])

        # Данные
        for registration in queryset:
            writer.writerow([
                registration.user.id,
                registration.tournament.title,
                registration.tournament.status,
                timezone.localtime(registration.tournament.started_at).strftime("%d.%m.%Y %H:%M"),
                registration.user.first_name,
                registration.user.username,
                registration.user.nickname,
                registration.user.phone,
                registration.knockouts,
                registration.points,
                timezone.localtime(registration.created_at).strftime("%d.%m.%Y %H:%M")
            ])

        return response


    @admin.display(description='Статус')
    def status_badge(self, obj):
        status_config = {
            'REGISTERED': ('🟢', 'green', 'Зарегистрирован'),
            'WAITLIST': ('🟡', 'yellow', 'В листе ожидания'),
            'CANCELLED': ('🔴', 'red', 'Отменена'),
        }
        emoji, color, text = status_config.get(obj.status, ('⚫', 'gray', obj.status))
        return format_html(
            '<span style="white-space: nowrap;">{} '
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">{}</span>'
            '</span>',
            emoji, color, text
        )

    @admin.display(ordering="tournament__status", description="Tournament status")
    def tournament_status(self, obj):
        return obj.tournament.status

    @admin.display(ordering="user__username", description="Username")
    def user_username(self, obj):
        return obj.user.username

    @admin.display(ordering="user__nickname", description="Nickname")
    def user_nickname(self, obj):
        return obj.user.nickname

    @admin.display(ordering="user__phone", description="Phone")
    def user_phone(self, obj):
        return obj.user.phone

    @admin.display(ordering='created_at', description='Зарегистрирован')
    def created_at_compact(self, obj):
        return timezone.localtime(obj.created_at).strftime('%d.%m.%Y %H:%M')


@admin.register(TournamentEventLog)
class TournamentEventLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'tournament', 'user_nickname', 'user_phone', 'display_event', 'count', 'multiplier', 'display_points', 'recorded_at', 'comment']
    list_filter = ['user', 'tournament', 'event', 'recorded_at', 'is_valid']
    search_fields = ['user__username', 'user__nickname', 'user__phone', 'tournament__title']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['user', 'tournament']

    def get_fieldsets(self, request, obj=None):
        fields = [
            ['Основная информация', {
                'fields': ['tournament', 'user', 'event', 'count', 'multiplier', 'display_points', 'recorded_at']
            }],
        ]

        if obj:
            fields.append(
                ['Даты', {
                    'fields': ['created_at', 'updated_at']
                }]
            )

        return fields

    @admin.display(ordering="user__username", description="Username")
    def user_username(self, obj):
        return obj.user.username

    @admin.display(ordering="user__nickname", description="Nickname")
    def user_nickname(self, obj):
        if obj.user:
            return obj.user.nickname

    @admin.display(ordering="user__phone", description="Phone")
    def user_phone(self, obj):
        if obj.user:
            return obj.user.phone

    @admin.display(description="Очки")  # ordering не будет работать для property
    def display_points(self, obj):
        return obj.points

    @admin.display(ordering="event", description="Событие")
    def display_event(self, obj):
        if obj.is_valid:
            return format_html("<p>{}</p>", obj.get_event_display())

        return format_html("<p style='color: red'>{}</p>", obj.get_event_display())

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
