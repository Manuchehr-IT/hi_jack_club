from rest_framework import serializers

from ..models import FAQ

class FAQSerializer(serializers.ModelSerializer):
	class Meta:
		model = FAQ
		# fields = "__all__"
		fields = ["id", "question", "answer", "sort_order"]
		read_only_fields = ["created_at", "updated_at"]
