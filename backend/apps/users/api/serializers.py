from rest_framework import serializers

from apps.telegram.utils import parse_telegram_init_data
from ..models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ["id", "username", "avatar_path", "nickname", "phone", "knockouts", "rating", "privacy_policy_accepted", "iiko_qr_code"]
		read_only_fields = ["knockouts", "rating", "privacy_policy_accepted", "created_at", "updated_at"]

class UserSignUpSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ["nickname", "phone", "privacy_policy_accepted"]

	def validate(self, attrs):
		required_fields = {"nickname", "phone", "privacy_policy_accepted"}

		missing = required_fields - attrs.keys()
		if missing:
			raise serializers.ValidationError({field: "This field is required." for field in missing})

		return attrs

	def validate_phone(self, value):
		return value.lstrip("+")

	def validate_privacy_policy_accepted(self, value):
		if value is not True:
			raise serializers.ValidationError("Privacy policy must be accepted.")
		return value

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
	# refresh = serializers.CharField()
	user = UserSerializer()
	is_new_user = serializers.BooleanField()
