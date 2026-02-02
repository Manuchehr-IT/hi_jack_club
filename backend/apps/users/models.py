import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

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
	knockouts = models.IntegerField(default=0, verbose_name="Нокауты")
	rating = models.IntegerField(default=0, verbose_name="Рейтинг")

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
		return f"{self.first_name} (ID: {self.id})"
