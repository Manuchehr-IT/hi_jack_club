import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from rest_framework import serializers

from apps.core.exceptions import CustomValidationError
from apps.telegram.utils import parse_telegram_init_data
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ["id", "username", "avatar_path", "nickname", "phone", "referral_code", "referrals", "knockouts", "rating", "privacy_policy_accepted", "iiko_qr_code"]
		read_only_fields = ["referral_code", "referrals", "knockouts", "rating", "privacy_policy_accepted", "created_at", "updated_at"]

class UpdateProfileSerializer(serializers.ModelSerializer):
	phone_code = serializers.CharField()

	class Meta:
		model = User
		fields = ["nickname", "phone_code", "phone"]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Access context in __init__ if needed
		self.is_signup = self.context.get("is_signup", False)

	def validate(self, attrs):
		if self.is_signup:
			required = ["nickname", "phone_code", "phone"]
			missing = [f for f in required if not attrs.get(f)]
			if missing:
				raise CustomValidationError(code="required_fields", message="Required fields", status_code=400, fields=missing)

		if not self.is_signup and not attrs.get("phone"):
			return attrs

		phone_code = attrs.get("phone_code", "")
		phone_number = attrs.get("phone", "")

		full_number = f"{phone_code}{phone_number}"
		try:
			parsed = phonenumbers.parse(full_number, None)
			if not phonenumbers.is_valid_number(parsed):
				raise CustomValidationError(code="invalid_phone_number", message="Invalid phone number", status_code=422, field="phone")
		except NumberParseException:
			raise CustomValidationError(code="incorrect_phone_format", message="Incorrect phone format", status_code=400, field="phone")

		attrs["phone"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
		attrs["phone_code"] = phone_code.strip()

		# ДОБАВЛЯЕМ ПРОВЕРКУ УНИКАЛЬНОСТИ ТЕЛЕФОНА ЗДЕСЬ!
		user = self.context.get("request").user if self.context.get("request") else None

		if User.objects.exclude(pk=user.pk if user else None).filter(phone=attrs["phone"]).exists():
			raise CustomValidationError(
				code="phone_already_taken",
				message="This phone number is already in use",
				status_code=409,
				field="phone",
				conflict_with="existing_user",
			)

		# if User.objects.exclude(pk=user.pk if user else None).filter(nickname=attrs["nickname"]).exists():
		# 	raise CustomValidationError(
		# 		code="nickname_already_taken",
		# 		message="This nickname is already occupied",
		# 		status_code=409,
		# 		field="nickname",
		# 		conflict_with="existing_user",
		# 	)

		return attrs

	def validate_nickname(self, value):
		nickname = value.strip()
		if not (3 <= len(nickname) <= 32):
			raise CustomValidationError(
				code="incorrect_nickname_length",
				message="Nickname cannot be less than 3 or more than 32 characters long",
				status_code=422,
				field="nickname",
			)

		user = None
		request = self.context.get('request')
		if request and hasattr(request, 'user'):
			user = request.user

		queryset = User.objects.all()
		if user and user.pk:
			queryset = queryset.exclude(pk=user.pk)

		if queryset.exclude(pk=user.pk if user else None).filter(nickname__iexact=nickname).exists():
			existing_user = queryset.filter(nickname__iexact=nickname).first()
			original_nickname = existing_user.nickname if existing_user else nickname

			raise CustomValidationError(
				code="nickname_already_taken",
				message=f"Nickname '{original_nickname}' is already taken",
				status_code=409,
				field="nickname",
				conflict_with="existing_user",
				existing_nickname=original_nickname  # дополнительная информация
			)

		return nickname

class TelegramAuthSerializer(serializers.Serializer):
	init_data = serializers.CharField()

	def validate_init_data(self, value):
		try:
			init_obj = parse_telegram_init_data(value)
			return init_obj
		except Exception as e:
			raise serializers.ValidationError(str(e))

class AuthResponseSerializer(serializers.Serializer):
	"""Для ДОКУМЕНТАЦИИ ответа (не для реального использования)"""
	access = serializers.CharField()
	refresh = serializers.CharField()
	user = UserSerializer()
	is_new_user = serializers.BooleanField()
