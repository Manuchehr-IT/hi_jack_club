from rest_framework import serializers

from ..models import SocialNetwork

class SocialNetworkSerializer(serializers.ModelSerializer):
	class Meta:
		model = SocialNetwork
		fields = "__all__"
		read_only_fields = ["updated_at"]
