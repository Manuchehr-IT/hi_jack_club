import logging
from decimal import ROUND_HALF_UP, Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db import transaction
from django.utils import timezone
from model_utils import FieldTracker
from typing import Tuple

logger = logging.getLogger(__name__)
User = get_user_model()

class TournamentRewardDistributionTemplate(models.Model):
	title = models.CharField(max_length=64, unique=True, verbose_name="Название")

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

	class Meta:
		verbose_name = "Шаблон распределения наград турнира"
		verbose_name_plural = "Шаблоны распределения наград турниров"

	def __str__(self):
		return f"{self.title}"


class TournamentRewardDistribution(models.Model):
	template = models.ForeignKey(TournamentRewardDistributionTemplate, on_delete=models.CASCADE, related_name="reward_distributions", verbose_name="Шаблон")

	position = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Позиция")
	percent = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))], default=Decimal("0.00"), verbose_name="Процент очков от общего банка")
	bonus_points = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], default=Decimal("0.00"), verbose_name="Бонусные очки")

	tracker = FieldTracker(fields=["position", "percent", "bonus_points"])

	class Meta:
		verbose_name = "Распределение наград турнира"
		verbose_name_plural = "Распределение наград турниров"
		unique_together = ["template", "position"]
		ordering = ["position"]

	def clean(self):
		if self.percent == 0 and self.bonus_points == 0:
			raise ValidationError("Должен быть указан хотя бы процент от банка или бонусные очки")

	def save(self, *args, **kwargs):
		self.full_clean()
		changed = self.tracker.changed()
		super().save(*args, **kwargs)

		if changed:
			logger.info(f"TournamentRewardDistribution tracker.changed: {changed}")

			tournaments = list(self.template.tournaments.all())
			for tournament in tournaments:
				transaction.on_commit(lambda t=tournament: t.recalc_all_registrations())

	def __str__(self):
		return f"{self.template.title} — {self.position} место: {self.percent}% + {self.bonus_points}"


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

	bank_points = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], default=Decimal("10000.00"), verbose_name="Общий банк очков")
	reward_distribution_template = models.ForeignKey(TournamentRewardDistributionTemplate, on_delete=models.SET_NULL, related_name="tournaments", null=True, blank=True, verbose_name="Шаблон распределения наград")

	status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.IN_QUEUE, verbose_name="Статус")

	icon = models.ImageField(upload_to="tournaments/icons/", blank=True, null=True, verbose_name="Иконка")

	olap_report_completed = models.BooleanField(default=False, verbose_name="OLAP отчет проведен")

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

	# Прочее
	tracker = FieldTracker(fields=["bank_points", "reward_distribution_template"])

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

	def save(self, *args, **kwargs):
		# self.full_clean()
		changed = self.tracker.changed()
		super().save(*args, **kwargs)

		if changed:
			logger.info(f"Tournament tracker.changed: {changed}")
			transaction.on_commit(lambda: self.recalc_all_registrations())

	def recalc_all_registrations(self):
		"""Пересчет всех регистраций турнира"""
		with transaction.atomic():
			for registration in self.registrations.all():
				registration.recalc_stats()

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

	def can_register(self, user) -> Tuple[bool, str]:
		"""Можно ли пользователю зарегистрироваться на турнир (по общим правилам)"""
		if not user:
			return False, "Пользователь не указан"

		if self.status != self.StatusType.IN_QUEUE:
			return False, "Регистрация закрыта"

		if self.registrations.filter(
			user=user,
			status__in=[
				TournamentRegistration.StatusType.REGISTERED,
				TournamentRegistration.StatusType.WAITLIST]
			).exists():
				return False, "Вы уже зарегистрированы"

		if self.get_participants_count() >= self.max_participants and self.get_waitlist_count() >= self.max_waitlist:
			return False, "Достигнут лимит участников"

		return True, ""

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

	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="registrations", verbose_name="Турнир")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tournament_registrations", verbose_name="Пользователь")
	status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.REGISTERED, verbose_name="Статус регистрации")

	# Игровая статистика
	knockouts = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="Нокауты")
	points = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="Очки рейтинга")
	rankings_calculated = models.BooleanField(default=False, verbose_name="Рейтинги учтены")

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

	# Дополнительные поля если нужно
	table_number = models.CharField(max_length=12, blank=True, null=True, verbose_name="Номер стола")
	attended = models.BooleanField(default=False, verbose_name="Пользователь присутствовал")

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

	def recalc_stats(self):
		"""Пересчитывает knockouts и points для данной регистрации"""
		events = TournamentEventLog.objects.filter(tournament=self.tournament, user=self.user)
		if not events:
			return

		colors = [i for i in TournamentEventLog.bounty_colors() if i != TournamentEventLog.EventType.BOUNTY_GOLD]
		# Суммируем нокауты (BOUNTY событий, кроме голда)
		knockouts = events.filter(
			event__in=colors
		).aggregate(
			total=models.Sum('count')
		)['total'] or Decimal("0")

		# Суммируем очки (используя свойство points)
		points = Decimal("0")
		for event in events:
			if event.event.startswith("BOUNTY_") or event.event == "ELIMINATION":
				points += event.points

		if self.knockouts != knockouts or self.points != points:
			with transaction.atomic():
				user = User.objects.select_for_update().get(pk=self.user.pk)
				registration = TournamentRegistration.objects.select_for_update().get(pk=self.pk)

				if registration.rankings_calculated:
					user.knockouts -= registration.knockouts
					user.points -= registration.points

				user.knockouts += knockouts
				user.points += points
				user.save(update_fields=["knockouts", "points"])

				print(f"> POINTS: {registration.points} -> {points}")
				registration.knockouts = knockouts
				registration.points = points
				registration.rankings_calculated = True
				registration.save(update_fields=["knockouts", "points", "rankings_calculated"])

	def __str__(self):
		return f"{self.user} - {self.tournament}"


class TournamentConfig(models.Model):
	tournament = models.OneToOneField(Tournament, on_delete=models.CASCADE, related_name="config", verbose_name="Турнир")
	entry_point = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], default=Decimal("100.00"), verbose_name="Очки за Entry (все)")
	add_on_point = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], default=Decimal("40.00"), verbose_name="Очки за Add-on")
	bounty_green_point = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], default=Decimal("25.00"), verbose_name="Очки за BountyGreen")
	bounty_blue_point = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], default=Decimal("50.00"), verbose_name="Очки за BountyBlue")
	bounty_red_point = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], default=Decimal("100.00"), verbose_name="Очки за BountyRed")
	bounty_gold_point = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], default=Decimal("50.00"), verbose_name="Очки за BountyGold")

	tracker = FieldTracker(fields=[
		"entry_point", "add_on_point", 
		"bounty_green_point", "bounty_blue_point", 
		"bounty_red_point", "bounty_gold_point"
	])

	class Meta:
		verbose_name = "Конфигурация турнира"
		verbose_name_plural = "Конфигурации турниров"

	@property
	def points_map(self) -> dict:
		"""Словарь всех очков для событий"""
		return {
			"ENTRY": self.entry_point, "RE_ENTRY": self.entry_point, "FREE_ENTRY": self.entry_point, "FREE_RE_ENTRY": self.entry_point, "FREE_ENTRY_DEP": self.entry_point,
			"ADD_ON": self.add_on_point,
			"BOUNTY_GREEN": self.bounty_green_point,
			"BOUNTY_BLUE": self.bounty_blue_point,
			"BOUNTY_RED": self.bounty_red_point,
			"BOUNTY_GOLD": self.bounty_gold_point,
		}

	def get_points(self, event_type: str) -> Decimal:
		"""Получить очки для события"""
		return self.points_map.get(event_type, Decimal("0.00"))

	def save(self, *args, **kwargs):
		changed = self.tracker.changed()
		super().save(*args, **kwargs)

		if changed:
			logger.info(f"TournamentConfig tracker.changed: {changed}")
			transaction.on_commit(lambda: self.tournament.recalc_all_registrations())


class TournamentEventLog(models.Model):
	class EventType(models.TextChoices):
		ENTRY = "ENTRY", "Entry"
		RE_ENTRY = "RE_ENTRY", "Re-entry"
		FREE_ENTRY = "FREE_ENTRY", "Free Entry"
		FREE_RE_ENTRY = "FREE_RE_ENTRY", "Free Re-entry"
		FREE_ENTRY_DEP = "FREE_ENTRY_DEP", "Free Entry Dep"
		ADD_ON = "ADD_ON", "Add-on"

		BOUNTY_GREEN = "BOUNTY_GREEN", "BountyGreen"
		BOUNTY_BLUE = "BOUNTY_BLUE", "BountyBlue"
		BOUNTY_RED = "BOUNTY_RED", "BountyRed"
		BOUNTY_GOLD = "BOUNTY_GOLD", "BountyGold"

		ELIMINATION = "ELIMINATION", "Elimination"

	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="events", verbose_name="Турнир")
	user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="tournament_events", blank=True, null=True, verbose_name="Пользователь")
	event = models.CharField(max_length=50, choices=EventType.choices, verbose_name="Событие")
	count = models.IntegerField(validators=[MinValueValidator(0)], default=1, verbose_name="Кол-во")
	multiplier = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], default=Decimal("1.00"), verbose_name="Множитель очков")
	recorded_at = models.DateTimeField(verbose_name="Дата записи")
	comment = models.CharField(max_length=256, blank=True, null=True, verbose_name="Комментарий")
	is_valid = models.BooleanField(default=True, verbose_name="Валидный для расчета")

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

	class Meta:
		verbose_name = "Журнал событий турнира"
		verbose_name_plural = "Журналы событий турниров"

	@classmethod
	def bounty_colors(cls):
		return [name for name in cls.EventType.names if name.startswith("BOUNTY_")]

	@property
	def points(self) -> Decimal:
		"""Вычисляет очки события на основе конфигурации турнира"""
		# if self.is_valid is False:
		# 	return Decimal("0.00")

		if self.event == self.EventType.ELIMINATION:
			elimination_events = list(TournamentEventLog.objects.filter(tournament=self.tournament, event=self.EventType.ELIMINATION).order_by("-recorded_at"))

			try:
				position = elimination_events.index(self) + 1
			except:
				return Decimal("0.00")

			rdt = self.tournament.reward_distribution_template
			if not rdt:
				return Decimal("0.00")

			reward_distribution = rdt.reward_distributions.filter(position=position).first()
			if not reward_distribution:
				return Decimal("0.00")

			entry_events_count = TournamentEventLog.objects.filter(
				tournament=self.tournament,
				event__in=[
					self.EventType.ENTRY,
					self.EventType.RE_ENTRY,
					self.EventType.FREE_ENTRY,
					self.EventType.FREE_RE_ENTRY,
					self.EventType.FREE_ENTRY_DEP,
					self.EventType.ADD_ON
				]
			).aggregate(total=models.Sum('count'))['total'] or 0

			total_bank_points = self.tournament.bank_points + (entry_events_count * self.tournament.config.entry_point)
			result = total_bank_points * (reward_distribution.percent / 100) + reward_distribution.bonus_points
		else:
			try:
				base_points = self.tournament.config.get_points(self.event)
				result = base_points * self.count * self.multiplier
			except TournamentConfig.DoesNotExist:
				print(f"> CONFIG NOT EXISTS for tournament {self.tournament_id}")
				return Decimal("0.00")

		return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
