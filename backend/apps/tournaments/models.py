from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from typing import Tuple

User = get_user_model()

class Tournament(models.Model):
	class StatusType(models.TextChoices):
		IN_QUEUE = "IN_QUEUE", "В очереди"
		ACTIVE = "ACTIVE", "Активный"
		INACTIVE = "INACTIVE", "Неактивный"

	title = models.CharField(max_length=64, verbose_name="Название")

	location = models.CharField(max_length=128, verbose_name="Локация")
	started_at = models.DateTimeField(verbose_name="Дата старта", help_text="Если указать прошедшую дату, статус автоматически станет 'Активный'")
	max_participants = models.PositiveIntegerField(default=60, verbose_name="Количество участников", help_text="Максимальное количество участников")
	max_waitlist = models.PositiveIntegerField(default=60, verbose_name="Количество ожидающих", help_text="Максимальное количество ожидающих")

	general_rules = models.TextField(verbose_name="Общие правила")

	status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.IN_QUEUE, verbose_name="Статус")

	icon = models.ImageField(upload_to="tournaments/icons/", blank=True, null=True, verbose_name="Иконка")

	olap_report_completed = models.BooleanField(default=False, verbose_name="OLAP отчет проведен")

	# Партнёрские интеграции (nenadengi и т.п.)
	buy_in = models.PositiveIntegerField(default=1000, blank=True, null=True, verbose_name="Бай-ин (₽)", help_text="0 — бесплатный турнир. Пусто оставлять нельзя: партнёры показывают «цена уточняется»")
	currency = models.CharField(max_length=3, default="RUB", verbose_name="Валюта")
	registerable = models.BooleanField(default=True, verbose_name="Доступен для записи у партнёров", help_text="Выключите для финалов/инвайтов — турнир виден в афише, но без кнопки записи")

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

	class Meta:
		verbose_name = "Турнир"
		verbose_name_plural = "Турниры"
		ordering = ["-created_at"]
		constraints = [
			models.UniqueConstraint(
				fields=["title", "started_at"],
				name="unique_tournament_title_per_date"
			)
		]

	# def clean(self):
	# 	super().clean()

	# 	# Запрещаем создавать турниры сразу с статусом INACTIVE
	# 	if not self.pk and self.status == self.StatusType.INACTIVE:
	# 		raise ValidationError({
	# 			"status": "Нельзя создать турнир сразу с статусом 'Неактивный'. Турнир должен пройти через статусы 'В очереди' или 'Активный'."
	# 		})

	# 	# Не изменяем статус если турнир уже завершен
	# 	if self.status == self.StatusType.INACTIVE:
	# 		return

	# 	now = timezone.now()

	# 	if self.started_at and self.started_at <= now:
	# 		self.status = self.StatusType.ACTIVE
	# 		self.started_at = now

	# 	elif self.started_at and self.started_at > now:
	# 		self.status = self.StatusType.IN_QUEUE

	# def save(self, *args, **kwargs):
	# 	self.full_clean()
	# 	super().save(*args, **kwargs)

	def get_participants_count(self):
		"""Количество зарегистрированных участников"""
		return self.registrations.filter(status=TournamentRegistration.StatusType.REGISTERED).count()

	def get_waitlist_count(self):
		"""Количество ожидающих участников"""
		return self.registrations.filter(status=TournamentRegistration.StatusType.WAITLIST).count()

	def compute_registration_status(self) -> str | None:
		"""Возвращает статус, куда нужно зарегистрировать пользователя."""
		if self.get_participants_count() < self.max_participants:
			return TournamentRegistration.StatusType.REGISTERED

		if self.get_waitlist_count() < self.max_waitlist:
			return TournamentRegistration.StatusType.WAITLIST

		return None

	def can_register(self, user) -> Tuple[bool, str, str | None]:
		"""Можно ли пользователю зарегистрироваться на турнир (по общим правилам).
		Третий элемент — машинный код причины отказа, для клиентов вроде бота."""
		if not user:
			return False, "Пользователь не указан", "NO_USER"

		if self.status != self.StatusType.IN_QUEUE:
			return False, "Регистрация закрыта", "REGISTRATION_CLOSED"

		if self.registrations.filter(
			user=user,
			status__in=[
				TournamentRegistration.StatusType.REGISTERED,
				TournamentRegistration.StatusType.WAITLIST]
			).exists():
				return False, "Вы уже зарегистрированы", "ALREADY_REGISTERED"

		if self.get_participants_count() >= self.max_participants and self.get_waitlist_count() >= self.max_waitlist:
			return False, "Достигнут лимит участников", "LIMIT_REACHED"

		return True, "", None

	@property
	def features(self):
		"""Для обратной совместимости с API"""
		return [feature.text for feature in self.features_list.all()]

	@features.setter
	def features(self, value):
		"""Устанавливает особенности из списка (для миграции)"""
		if isinstance(value, list):
			self.features_list.all().delete()
			for i, text in enumerate(value):
				TournamentFeature.objects.create(
					tournament=self,
					text=text,
					order=i
				)

	def __str__(self):
		return f"{self.title} - {timezone.localtime(self.started_at).strftime('%d.%m.%Y %H:%M')}"


class TournamentFeature(models.Model):
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="features_list")
	text = models.CharField(max_length=256, verbose_name="Текст особенности")
	sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

	class Meta:
		verbose_name = "Особенность турнира"
		verbose_name_plural = "Особенности турнира"
		ordering = ["sort_order"]

	def __str__(self):
		return f"Особенность #{self.id}"
		# return self.text[:50]  # Показываем первые 50 символов


class TournamentRegistration(models.Model):
	"""Промежуточная модель для регистрации на турниры"""
	class StatusType(models.TextChoices):
		REGISTERED = "REGISTERED", "Зарегистрирован"
		WAITLIST = "WAITLIST", "В листе ожидания"

	class SourceType(models.TextChoices):
		NENADENGI = "nenadengi", "nenadengi"
		# в будущем, если появится ещё один партнёр, у которого есть бронирование — новый пункт сюда

	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="registrations", verbose_name="Турнир")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tournament_registrations", verbose_name="Пользователь")
	status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.REGISTERED, verbose_name="Статус регистрации")

	# Игровая статистика
	knockouts = models.IntegerField(default=0, verbose_name="Нокауты")
	points = models.IntegerField(default=0, verbose_name="Очки рейтинга")
	attended = models.BooleanField(default=False, verbose_name="Пользователь присутствовал")
	place = models.PositiveIntegerField(blank=True, null=True, verbose_name="Место")
	payout = models.PositiveIntegerField(blank=True, null=True, verbose_name="Приз (₽)")

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

	# Дополнительные поля если нужно
	table_number = models.CharField(max_length=12, blank=True, null=True, verbose_name="Номер стола")

	# Откуда пришла регистрация: None — своя (бот/апп), иначе код партнёра
	source = models.CharField(max_length=32, choices=SourceType.choices, blank=True, null=True, default=None, verbose_name="Источник")

	class Meta:
		verbose_name = "Регистрация на турнир"
		verbose_name_plural = "Регистрации на турниры"
		unique_together = ["tournament", "user"]
		ordering = ["created_at"]

	def get_waitlist_position(self):
		if self.status != self.StatusType.WAITLIST:
			return None

		# Считаем сколько записей в ожидании создано раньше текущей
		position = TournamentRegistration.objects.filter(
			tournament=self.tournament,
			status=self.StatusType.WAITLIST,
			created_at__lt=self.created_at
		).count()

		# +1 потому что позиции начинаются с 1, а не с 0
		return position + 1

	def __str__(self):
		return f"{self.user} - {self.tournament}"


class PartnerRegistration(models.Model):
	"""Бронь турнира, пришедшая от партнёра (nenadengi). До связывания с нашим
	User хранит снэпшот гостя и его результат сама; после связывания вся
	дальнейшая судьба очков/нокаутов идёт через обычную TournamentRegistration."""

	class StatusType(models.TextChoices):
		CONFIRMED = "confirmed", "Подтверждена"
		WAITLISTED = "waitlisted", "Лист ожидания"
		REJECTED = "rejected", "Отклонена"
		CANCELLED = "cancelled", "Отменена гостем"

	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="partner_registrations", verbose_name="Турнир")

	# Идентификация гостя на стороне nenadengi
	partner_player_id = models.UUIDField(db_index=True, verbose_name="ID гостя у партнёра")
	partner_registration_id = models.CharField(max_length=64, unique=True, verbose_name="ID брони у партнёра")

	# Снэпшот гостя на момент этой конкретной брони
	nickname = models.CharField(max_length=64, verbose_name="Никнейм у партнёра")
	name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Имя")
	tg_username = models.CharField(max_length=32, blank=True, null=True, verbose_name="Telegram username")

	# Связь с нашей системой — пусто, пока админ (или авто-линковка по nenadengi_id) не свяжет
	user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="partner_registrations", verbose_name="Пользователь")
	tournament_registration = models.OneToOneField(
		TournamentRegistration, on_delete=models.SET_NULL, blank=True, null=True,
		related_name="partner_registration", verbose_name="Регистрация"
	)

	status = models.CharField(max_length=20, choices=StatusType.choices, verbose_name="Статус брони")
	seat = models.CharField(max_length=12, blank=True, null=True, verbose_name="Место")
	is_test = models.BooleanField(default=False, verbose_name="Тестовая бронь")

	# Результат — актуален только пока tournament_registration не проставлена
	attended = models.BooleanField(default=False, verbose_name="Присутствовал")
	place = models.PositiveIntegerField(blank=True, null=True, verbose_name="Место в турнире")
	payout = models.PositiveIntegerField(blank=True, null=True, verbose_name="Приз (₽)")

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

	class Meta:
		verbose_name = "Партнёрская бронь"
		verbose_name_plural = "Партнёрские брони"
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.nickname} ({self.partner_player_id}) - {self.tournament}"
