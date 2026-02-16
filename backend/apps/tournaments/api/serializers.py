from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models import Tournament, TournamentRegistration
from apps.users.api.serializers import UserSerializer

User = get_user_model()

class TournamentSerializer(serializers.ModelSerializer):
	features = serializers.ListField(child=serializers.CharField(max_length=256), required=False, default=list, help_text="Список особенностей турнира")

	class Meta:
		model = Tournament
		fields = "__all__"
		read_only_fields = ["status", "created_at", "updated_at"]

class TournamentRegistrationSerializer(serializers.ModelSerializer):
	user = UserSerializer(read_only=True)
	waitlist_position = serializers.SerializerMethodField()

	class Meta:
		model = TournamentRegistration
		fields = ["id", "user", "status", "table_number", "created_at", "waitlist_position"]
		ordering = ["created_at"]

	def get_waitlist_position(self, obj):
		"""Возвращает позицию только если статус WAITLIST"""
		if obj.status == TournamentRegistration.StatusType.WAITLIST:
			return TournamentRegistration.objects.filter(
				tournament=obj.tournament,
				status=TournamentRegistration.StatusType.WAITLIST,
				created_at__lt=obj.created_at
			).count() + 1
		return None
