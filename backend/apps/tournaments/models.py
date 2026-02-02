import os
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()

def validate_image_or_svg(file):
	valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg']
	ext = os.path.splitext(file.name)[1].lower()
	if ext not in valid_extensions:
		raise ValidationError('Неподдерживаемый формат файла.')

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

	# Иконка
	icon = models.ImageField(upload_to="tournaments/icons/", blank=True, null=True, verbose_name="Иконка")

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

	def can_register(self, user):
		"""Можно ли зарегистрироваться на турнир"""
		if not user or not user.id:
			return False, "Пользователь не указан"

		if self.status != self.StatusType.IN_QUEUE:
			return False, "Регистрация возможна только для турниров в очереди"
		if self.get_participants_count() >= self.max_participants: # Исправить и добавить WAITLIST
			return False, "Достигнуто максимальное количество участников"
		if self.registrations.filter(user=user, status__in=[TournamentRegistration.StatusType.REGISTERED, TournamentRegistration.StatusType.WAITLIST]).exists():
			return False, "Вы уже зарегистрированы на этот турнир"
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
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

	# Дополнительные поля если нужно
	table_number = models.CharField(max_length=12, blank=True, null=True, verbose_name="Номер стола")

	class Meta:
		verbose_name = "Регистрация на турнир"
		verbose_name_plural = "Регистрации на турниры"
		unique_together = ["tournament", "user"]
		ordering = ["created_at"]

	def clean(self):
		super().clean()

		# Проверяем, что регистрация возможна
		if not self.pk: # Только для новых регистраций
			if not self.tournament_id:
				raise ValidationError("Необходимо выбрать турнир")

			can_register, message = self.tournament.can_register(self.user)
			if not can_register:
				raise ValidationError(message)

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.user} - {self.tournament}"
