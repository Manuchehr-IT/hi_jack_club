from typing import List, Self
import uuid
from decimal import Decimal
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

class UserManager(BaseUserManager):
	def create_user(self, telegram_id: int, first_name: str, password: str | None = None, **extra_fields):
		if not telegram_id:
			raise ValueError("Telegram ID must be set")
		if not first_name:
			raise ValueError("First name must be set")

		nickname = self._generate_nickname(telegram_id=telegram_id)
		if User.objects.filter(nickname=nickname).exists():
			nickname = self._generate_unique_nickname(base_nickname=nickname)

		user = self.model(telegram_id=telegram_id, first_name=first_name, nickname=nickname, **extra_fields)

		if password:
			user.set_password(password)
		else:
			user.set_unusable_password()
		user.save(using=self._db)
		return user

	def create_superuser(self, telegram_id: int, first_name: str, password: str, **extra_fields):
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("is_staff", True)

		if password is None:
			raise ValueError("Superuser must have a password")

		user = self.create_user(telegram_id=telegram_id, first_name=first_name, password=password, **extra_fields)
		return user

	def _generate_nickname(self, telegram_id: int) -> str:
		"""Генерирует базовый nickname"""
		return f"user_{telegram_id}"

	def _generate_unique_nickname(self, base_nickname: str) -> str:
		"""Генерирует уникальный nickname если базовый занят"""
		counter = 1
		while True:
			new_nickname = f"{base_nickname}_{counter}"
			if not User.objects.filter(nickname=new_nickname).exists():
				return new_nickname
			counter += 1

class User(AbstractBaseUser, PermissionsMixin):
	telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
	first_name = models.CharField(max_length=64, verbose_name="Имя")
	username = models.CharField(max_length=32, blank=True, null=True, verbose_name="Username")
	language_code = models.CharField(max_length=2, default="ru", verbose_name="Язык")
	avatar_path = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Аватар")
	nickname = models.CharField(max_length=32, unique=True, verbose_name="Никнейм")
	phone = models.CharField(max_length=16, unique=True, blank=True, null=True, verbose_name="Телефон")

	# Рефералка
	referrer = models.ForeignKey("self", blank=True, null=True, on_delete=models.DO_NOTHING, related_name="referrals", verbose_name="Реферер")
	referral_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="Реферальный код")

	# Игровая статистика
	knockouts = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Нокауты")
	points = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="Очки рейтинга")

	# iiko:
	iiko_id = models.UUIDField(unique=True, blank=True, null=True, verbose_name="Iiko ID")
	iiko_qr_code = models.ImageField(upload_to="iiko_qr_codes/", null=True, blank=True, verbose_name="Статические QR")

	# Соглашения
	privacy_policy_accepted = models.BooleanField(default=False, verbose_name="Согласие на политику конфиденциальности")

	# Системные поля (только необходимые)
	is_active = models.BooleanField(default=True, verbose_name="Активен")
	is_staff = models.BooleanField(default=False, verbose_name="Доступ в админку")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

	groups = models.ManyToManyField("auth.Group", blank=True, related_name="custom_user_set")
	user_permissions = models.ManyToManyField("auth.Permission", blank=True, related_name="custom_user_permissions_set")

	objects = UserManager()

	USERNAME_FIELD = "telegram_id"
	REQUIRED_FIELDS = ["first_name"]

	class Meta:
		verbose_name = "Пользователь"
		verbose_name_plural = "Пользователи"
		ordering = ["-created_at"]

	def __str__(self):
		info = []
		if self.nickname:
			info.append(f"{self.nickname}")
		if self.phone:
			info.append(f"{self.phone}")
		if self.username:
			info.append(f"@{self.username}")

		if info:
			return " | ".join(info)

		return f"{self.first_name} (ID: {self.id})"

class UserRewardLog(models.Model):
	class OperationType(models.TextChoices):
		CREDITING = "CREDITING", "Зачисление"
		DEDUCTING = "DEDUCTING", "Списание"

	class RewardType(models.TextChoices):
		KNOCKOUTS = "KNOCKOUTS", "Knockouts"
		POINTS = "POINTS", "Points"

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rewards", verbose_name="Пользователь")
	operation = models.CharField(max_length=50, choices=OperationType.choices, verbose_name="Тип операции")
	reward = models.CharField(max_length=50, choices=RewardType.choices, verbose_name="Тип награды")
	count = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], verbose_name="Кол-во")
	comment = models.CharField(max_length=256, blank=True, null=True, verbose_name="Комментарий")

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

	class Meta:
		verbose_name = "Журнал наград пользователя"
		verbose_name_plural = "Журналы наград пользователей"

	def get_rewards(self, tournament, reward) -> List[Self]:
		return UserRewardLog.objects.filter(tournament=tournament, reward=reward).order_by("-created_at")

	def clean(self):
		if self.count == 0:
			raise ValidationError("Количество наград не может быть 0")

	def save(self, *args, **kwargs):
		self.full_clean()
		self._update_user_reward()
		super().save(*args, **kwargs)

	def _update_user_reward(self):
		if self.reward == self.RewardType.KNOCKOUTS:
			self.user.knockouts = self.user.knockouts + self.count if self.operation == self.OperationType.CREDITING else self.user.knockouts - self.count

		elif self.reward == self.RewardType.POINTS:
			self.user.points = self.user.points + self.count if self.operation == self.OperationType.CREDITING else self.user.points - self.count

		self.user.save()

