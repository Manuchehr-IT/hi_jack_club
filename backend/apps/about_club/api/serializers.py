from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..models import AboutClub, AboutClubImage

class AboutClubImageSerializer(serializers.ModelSerializer):
	url = serializers.ImageField(source="image", read_only=True)

	class Meta:
		model = AboutClubImage
		fields = ["id", "alt", "sort_order", "uploaded_at", "url"]

class AboutClubSerializer(serializers.ModelSerializer):
	images = AboutClubImageSerializer(many=True, source="block_images", read_only=True)

	get_image_count = serializers.SerializerMethodField()

	class Meta:
		model = AboutClub
		fields = ["id", "sort_order", "text", "is_active", "images", "get_image_count"]

	@extend_schema_field(serializers.IntegerField())  # для OpenAPI
	def get_get_image_count(self, obj) -> int:
		return obj.get_image_count()
