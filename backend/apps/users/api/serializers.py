import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from rest_framework import serializers

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
		self.is_signup = self.context.get('is_signup', False)

	def validate(self, attrs):
		if self.is_signup:
			required = ["nickname", "phone_code", "phone"]
			missing = [f for f in required if not attrs.get(f)]
			if missing:
				raise serializers.ValidationError({field: "This field is required." for field in missing})

		if not self.is_signup and not attrs.get("phone"):
			return attrs

		phone_code = attrs.get("phone_code", "")
		phone_number = attrs.get("phone", "")

		full_number = f"{phone_code}{phone_number}"
		try:
			parsed = phonenumbers.parse(full_number, None)
			if not phonenumbers.is_valid_number(parsed):
				raise serializers.ValidationError("Invalid phone number")
		except NumberParseException:
			raise serializers.ValidationError("Incorrect phone format")

		attrs["phone"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
		attrs["phone_code"] = phone_code.strip()
		return attrs

	def validate_nickname(self, value):
		nickname = value.strip()
		if not (3 <= len(nickname) <= 32):
			raise serializers.ValidationError("Nickname cannot be less than 3 or more than 32 characters long.")

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
