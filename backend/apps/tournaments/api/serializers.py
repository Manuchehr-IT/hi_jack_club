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

	class Meta:
		model = TournamentRegistration
		fields = ["id", "user", "status", "table_number", "created_at"]
		ordering = ["created_at"]
