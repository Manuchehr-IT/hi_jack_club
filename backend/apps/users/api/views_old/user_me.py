from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.api.serializers import UserSerializer, UpdateProfileSerializer

@extend_schema(
	tags=["Users"],
	summary="Получить/обновить пользователя",
	responses={200: UserSerializer}
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
	"""
	GET, PATCH /api/users/me/
	"""
	if request.method == "GET":
		serializer = UserSerializer(request.user)
		return Response(serializer.data)

	elif request.method == "PATCH":
		serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True, context={"request": request})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(UserSerializer(request.user).data)

