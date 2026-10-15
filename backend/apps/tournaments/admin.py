import openpyxl
from io import BytesIO

from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html
from django.utils import timezone

from .models import PartnerRegistration, Tournament, TournamentFeature, TournamentRegistration
from .signals import recalculate_user_rating


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
    extra = 1
    ordering = ('sort_order',)
    min_num = 0

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('sort_order')


def _normalize_phone(phone) -> str:
    """79153530163 → +79153530163"""
    s = str(phone).strip()
    if s and not s.startswith('+'):
        s = '+' + s
    return s


def _find_col(headers_lower: list[str], candidates: list[str]) -> int | None:
    for name in candidates:
        try:
            return headers_lower.index(name)
        except ValueError:
            pass
    return None


def _to_int(val) -> int:
    """Конвертирует значение ячейки в int. Обрабатывает int, float, строки вида '25', '25.0', '25,5'."""
    if val is None:
        return 0
    if isinstance(val, bool):
        return int(val)
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val).strip().replace(',', '.')
    if not s:
        return 0
    return int(float(s))


def _parse_excel(file) -> tuple[list[dict], list[str]]:
    """
    Парсит Excel с результатами турнира (файл содержит только реальных участников).
    data_only=True — читает кешированные результаты формул, а не сами формулы.
    Возвращает (rows, errors) — все строки с валидными ИГР Рейт/ИГР Кил, включая 0/0:
    наличие строки в отчёте само по себе означает участие в турнире.
    """
    wb = openpyxl.load_workbook(BytesIO(file.read()), data_only=True)
    ws = wb.active
    if ws is None:
        return [], ["Не удалось открыть лист Excel"]

    # Ищем строку с заголовками в первых 5 строках
    header_row_num = None
    hl = []
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=5, values_only=True), start=1):
        row_lower = [str(v).strip().lower() if v is not None else '' for v in row]
        if 'игр рейт' in row_lower or 'игр_рейт' in row_lower or 'points' in row_lower:
            header_row_num = i
            hl = row_lower
            break

    if header_row_num is None:
        return [], ["Не найдена строка с заголовками (ищу 'ИГР Рейт' в первых 5 строках)"]

    id_idx        = _find_col(hl, ['id'])
    phone_idx     = _find_col(hl, ['phone', 'телефон'])
    nickname_idx  = _find_col(hl, ['nickname', 'никнейм'])
    points_idx    = _find_col(hl, ['игр рейт', 'игр_рейт', 'points'])
    knockouts_idx = _find_col(hl, ['игр кил', 'игр_кил', 'knockouts'])
    # Опциональные колонки — если их нет в файле, place/payout останутся пустыми
    place_idx     = _find_col(hl, ['место', 'place'])
    payout_idx    = _find_col(hl, ['приз', 'payout', 'выигрыш'])

    errors = []
    if points_idx is None:
        errors.append("Не найдена колонка 'ИГР Рейт' (или 'points')")
    if knockouts_idx is None:
        errors.append("Не найдена колонка 'ИГР Кил' (или 'knockouts')")
    if errors:
        return [], errors

    rows = []
    place_counter = 0
    for row_num, row in enumerate(ws.iter_rows(min_row=header_row_num + 1, values_only=True), start=header_row_num + 1):
        if not any(v is not None for v in row):
            continue

        # Счётчик строки — независимо от дальнейших ошибок парсинга, чтобы места
        # у всех остальных участников не съезжали, если одна строка не читается
        place_counter += 1

        try:
            points    = _to_int(row[points_idx])
            knockouts = _to_int(row[knockouts_idx])
        except (ValueError, TypeError) as e:
            errors.append(f'Строка {row_num}: не удалось прочитать ИГР Рейт/ИГР Кил — {e}')
            continue

        user_id  = _to_int(row[id_idx]) if id_idx is not None and row[id_idx] is not None else None
        phone    = _normalize_phone(row[phone_idx]) if phone_idx is not None and row[phone_idx] else ''
        nickname = str(row[nickname_idx]).strip().lower() if nickname_idx is not None and row[nickname_idx] else ''
        # Явная колонка места — если вдруг появится в файле; иначе берём порядок
        # строк в отчёте (админ выгружает уже отсортированным: 1-я строка — победитель)
        if place_idx is not None and row[place_idx] is not None:
            place = _to_int(row[place_idx])
        else:
            place = place_counter
        payout   = _to_int(row[payout_idx]) if payout_idx is not None and row[payout_idx] is not None else None

        rows.append({
            'user_id': user_id or None,
            'phone': phone,
            'nickname': nickname,
            'points': points,
            'knockouts': knockouts,
            'place': place or None,
            'payout': payout or None,
        })

    return rows, errors


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
        if obj:
            return (
                ('Основная информация', {
                    'fields': ('title', 'location', 'started_at', 'general_rules', 'max_participants', 'max_waitlist', 'icon')
                }),
                ('Партнёрская афиша (nenadengi и т.п.)', {
                    'fields': ('buy_in', 'currency', 'registerable')
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
                'fields': ('title', 'location', 'started_at', 'general_rules', 'max_participants', 'max_waitlist', 'icon')
            }),
            ('Партнёрская афиша (nenadengi и т.п.)', {
                'fields': ('buy_in', 'currency', 'registerable')
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
        if not obj:
            return []

        readonly_fields = ['created_at', 'updated_at', 'status_display', 'participants_count_display']

        if obj.status == 'INACTIVE':
            all_fields = [f.name for f in self.model._meta.fields if f.name != 'started_at']
            readonly_fields = all_fields + ['status_display', 'participants_count_display']

        return readonly_fields

    def get_exclude(self, request, obj=None):
        if not obj:
            return ['status']
        return []

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
        elif obj.status == 'INACTIVE':
            return format_html(
                '<a class="button" href="upload_results/{}/" style="background: #007bff; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">Загрузить результаты</a>',
                obj.id
            )
        return ""
    tournament_action_button.short_description = 'Действие'

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
            path(
                'upload_results/<int:tournament_id>/',
                self.admin_site.admin_view(self.upload_results),
                name='upload_results'
            ),
        ]
        return custom_urls + urls

    def start_tournament(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            tournament.started_at = timezone.now()
            tournament.status = 'ACTIVE'
            tournament.save()
            self.message_user(request, f'Турнир "{tournament.title}" успешно запущен', messages.SUCCESS)
        except Tournament.DoesNotExist:
            self.message_user(request, 'Турнир не найден', messages.ERROR)

        return redirect('admin:tournaments_tournament_changelist')

    def finish_tournament(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            tournament.status = 'INACTIVE'
            tournament.save()
            self.message_user(request, f'Турнир "{tournament.title}" успешно завершен', messages.SUCCESS)
        except Tournament.DoesNotExist:
            self.message_user(request, 'Турнир не найден', messages.ERROR)

        return redirect('admin:tournaments_tournament_changelist')

    def upload_results(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            self.message_user(request, 'Турнир не найден', messages.ERROR)
            return redirect('admin:tournaments_tournament_changelist')

        if tournament.status != Tournament.StatusType.INACTIVE:
            self.message_user(request, 'Загрузка результатов доступна только для завершённых турниров.', messages.ERROR)
            return redirect('admin:tournaments_tournament_changelist')

        context = {
            **self.admin_site.each_context(request),
            'tournament': tournament,
            'title': f'Загрузить результаты: {tournament.title}',
            'result': None,
            'errors': [],
        }

        if request.method != 'POST' or not request.FILES.get('excel_file'):
            return render(request, 'admin/tournaments/upload_results.html', context)

        try:
            rows, parse_errors = _parse_excel(request.FILES['excel_file'])
        except Exception as e:
            self.message_user(request, f'Ошибка чтения файла: {e}', messages.ERROR)
            return render(request, 'admin/tournaments/upload_results.html', context)

        if parse_errors and not rows:
            context['errors'] = parse_errors
            return render(request, 'admin/tournaments/upload_results.html', context)

        if not rows:
            self.message_user(request, 'В файле нет строк с результатами', messages.WARNING)
            return render(request, 'admin/tournaments/upload_results.html', context)

        # Индекс регистраций по user_id, phone, nickname
        regs_by_user_id  = {}
        regs_by_phone    = {}
        regs_by_nickname = {}
        for reg in TournamentRegistration.objects.filter(tournament=tournament).select_related('user'):
            regs_by_user_id[reg.user_id] = reg
            if reg.user.phone:
                regs_by_phone[reg.user.phone.strip()] = reg
            regs_by_nickname[reg.user.nickname.strip().lower()] = reg

        # Ещё не связанные брони партнёра (nenadengi) этого турнира — fallback по нику
        partner_regs_by_nickname = {
            partner_reg.nickname.strip().lower(): partner_reg
            for partner_reg in PartnerRegistration.objects.filter(tournament=tournament, tournament_registration__isnull=True)
        }

        from django.contrib.auth import get_user_model
        User = get_user_model()

        to_update = []
        to_create = []
        partner_to_update = []
        affected_user_ids = set()
        errors = list(parse_errors)

        for row in rows:
            reg = (
                regs_by_user_id.get(row['user_id'])
                or regs_by_phone.get(row['phone'])
                or regs_by_nickname.get(row['nickname'])
            )

            if reg is not None:
                reg.knockouts = row['knockouts']
                reg.points = row['points']
                reg.place = row['place']
                reg.payout = row['payout']
                reg.attended = True
                to_update.append(reg)
                affected_user_ids.add(reg.user_id)
                continue

            # Регистрации нет — ищем пользователя для авто-регистрации
            user = None
            if row['user_id']:
                user = User.objects.filter(pk=row['user_id']).first()
            if not user and row['phone']:
                user = User.objects.filter(phone=row['phone']).first()
            if not user and row['nickname']:
                user = User.objects.filter(nickname__iexact=row['nickname']).first()

            if user:
                to_create.append(TournamentRegistration(
                    tournament=tournament,
                    user=user,
                    status=TournamentRegistration.StatusType.REGISTERED,
                    points=row['points'],
                    knockouts=row['knockouts'],
                    place=row['place'],
                    payout=row['payout'],
                    attended=True,
                ))
                affected_user_ids.add(user.id)
                continue

            # Пользователя у нас нет — может, это гость nenadengi, ещё не связанный с нашим User
            partner_reg = partner_regs_by_nickname.get(row['nickname'])
            if partner_reg:
                partner_reg.attended = True
                partner_reg.place = row['place']
                partner_reg.payout = row['payout']
                partner_to_update.append(partner_reg)
                continue

            identifier = row['phone'] or row['nickname'] or f"ID={row['user_id']}"
            errors.append(f'Пользователь не найден: «{identifier}» (ИГР Рейт={row["points"]}, ИГР Кил={row["knockouts"]})')

        # Сброс всех регистраций турнира перед применением нового файла,
        # чтобы пользователи из предыдущей загрузки не сохраняли старые очки.
        all_reg_user_ids = set(
            TournamentRegistration.objects.filter(tournament=tournament).values_list('user_id', flat=True)
        )
        TournamentRegistration.objects.filter(tournament=tournament).update(
            points=0, knockouts=0, place=None, payout=None, attended=False
        )
        PartnerRegistration.objects.filter(tournament=tournament, tournament_registration__isnull=True).update(
            attended=False, place=None, payout=None
        )

        if to_update:
            TournamentRegistration.objects.bulk_update(to_update, ['knockouts', 'points', 'place', 'payout', 'attended'])

        if to_create:
            TournamentRegistration.objects.bulk_create(to_create)

        if partner_to_update:
            PartnerRegistration.objects.bulk_update(partner_to_update, ['attended', 'place', 'payout'])

        # Пересчитываем всех, у кого были или появились очки
        for user_id in all_reg_user_ids | affected_user_ids:
            recalculate_user_rating(user_id)

        # Если в файле были строки, но ни одна не замэтчилась — скорее всего загрузили
        # не тот файл. Не отправляем в nenadengi пустой ростер, пусть админ разберётся.
        if to_update or to_create or partner_to_update:
            from celery_app.tasks.nenadengi import sync_results_task
            sync_results_task.delay(tournament.id)

        context['result'] = {'updated': len(to_update), 'created': len(to_create)}
        context['errors'] = errors

        if to_update or to_create:
            self.message_user(
                request,
                f'Обновлено {len(to_update)} регистраций, создано {len(to_create)} новых.',
                messages.SUCCESS,
            )

        return render(request, 'admin/tournaments/upload_results.html', context)

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
    list_filter = ['status', 'tournament', 'created_at']
    search_fields = ['user__username', 'user__nickname', 'tournament__title']
    readonly_fields = ['created_at', 'updated_at']
    exclude = ['attended']
    list_select_related = ['user', 'tournament']

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

    @admin.display(ordering="user__nickname", description="Nickname")
    def user_nickname(self, obj):
        return obj.user.nickname

    @admin.display(ordering="user__username", description="Username")
    def user_username(self, obj):
        return obj.user.username

    @admin.display(ordering="user__phone", description="Phone")
    def user_phone(self, obj):
        return obj.user.phone

    @admin.display(ordering='created_at', description='Зарегистрирован')
    def created_at_compact(self, obj):
        return timezone.localtime(obj.created_at).strftime('%d.%m.%Y %H:%M')


@admin.register(PartnerRegistration)
class PartnerRegistrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'tournament', 'nickname', 'partner_player_id', 'user', 'status', 'attended', 'is_test', 'created_at_compact']
    list_filter = ['status', 'is_test', 'tournament']
    search_fields = ['nickname', 'name', 'tg_username', 'partner_player_id', 'partner_registration_id']
    readonly_fields = ['partner_player_id', 'partner_registration_id', 'nickname', 'name', 'tg_username', 'tournament_registration', 'created_at', 'updated_at']
    autocomplete_fields = ['user']
    list_select_related = ['user', 'tournament']
    actions = ['unlink_selected']

    @admin.display(ordering='created_at', description='Создана')
    def created_at_compact(self, obj):
        return timezone.localtime(obj.created_at).strftime('%d.%m.%Y %H:%M')

    @admin.action(description='Отвязать от пользователя (откатить ошибочную линковку)')
    def unlink_selected(self, request, queryset):
        from .partner_integration import unlink_partner_registration

        count = 0
        for partner_reg in queryset.filter(user__isnull=False):
            unlink_partner_registration(partner_reg)
            count += 1

        self.message_user(request, f'Отвязано: {count}.', messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        from .partner_integration import link_partner_registration, unlink_partner_registration

        previous = PartnerRegistration.objects.filter(pk=obj.pk).first() if change else None
        previous_user_id = previous.user_id if previous else None

        # Пользователя в форме очистили — это отвязка, а не обычное сохранение
        if previous and previous_user_id and not obj.user_id:
            unlink_partner_registration(previous)
            obj.tournament_registration = None
            super().save_model(request, obj, form, change)
            self.message_user(request, 'Связь с пользователем снята.', messages.SUCCESS)
            return

        super().save_model(request, obj, form, change)

        if obj.user_id and obj.user_id != previous_user_id:
            link_partner_registration(obj, obj.user)
            self.message_user(
                request,
                'Гость связан с пользователем. Если результаты этого турнира уже загружались — загрузите тот же Excel-файл повторно, чтобы очки попали в обычную регистрацию.',
                messages.SUCCESS,
            )
