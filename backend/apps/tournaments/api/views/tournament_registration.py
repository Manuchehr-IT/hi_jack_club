from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tournaments.models import Tournament, TournamentRegistration
from apps.tournaments.api.serializers import TournamentRegistrationSerializer
from apps.tournaments.api.views.tournament_lifecycle import InternalApiPermission
from celery_app.tasks.telegram import send_telegram
from celery_app.tasks.telegram.schemas import SendMethod

User = get_user_model()

def _perform_registration(pk, user):
	"""Общая логика регистрации на турнир. Возвращает (registration, error_response)."""
	with transaction.atomic():
		tournament = Tournament.objects.select_for_update().filter(pk=pk).first()
		if not tournament:
			return None, Response({"detail": "Турнир не найден", "code": "NOT_FOUND"}, status=404)

		can, error, code = tournament.can_register(user)
		if not can:
			return None, Response({"detail": error, "code": code}, status=400)

		status_type = tournament.compute_registration_status()
		if not status_type:
			return None, Response({"detail": "Достигнут лимит участников", "code": "LIMIT_REACHED"}, status=400)

		registration = TournamentRegistration.objects.create(
			tournament=tournament,
			user=user,
			status=status_type
		)

	return registration, None

def _perform_unregistration(pk, user):
	"""Общая логика отмены регистрации на турнир. Возвращает (unregistered, error_response)."""
	with transaction.atomic():
		tournament = Tournament.objects.select_for_update().filter(pk=pk).first()
		if not tournament:
			return False, Response({"detail": "Турнир не найден", "code": "NOT_FOUND"}, status=404)

		if tournament.status != Tournament.StatusType.IN_QUEUE:
			return False, Response({"detail": "Регистрация закрыта", "code": "REGISTRATION_CLOSED"}, status=400)

		if not TournamentRegistration.objects.filter(tournament=tournament, user=user).exists():
			return False, Response({"detail": "Вы не зарегистрированы на этот турнир", "code": "NOT_REGISTERED"}, status=400)

		old_waitlist = TournamentRegistration.objects.filter(
			tournament=tournament,
			status=TournamentRegistration.StatusType.WAITLIST
		).order_by("created_at")

		old_position_telegram_ids = {position: registration.user.telegram_id for position, registration in enumerate(old_waitlist[:5], start=1)}

		TournamentRegistration.objects.filter(tournament=tournament, user=user).delete()

		if tournament.get_participants_count() < tournament.max_participants:
			first_in_line = TournamentRegistration.objects.filter(
				tournament=tournament,
				status=TournamentRegistration.StatusType.WAITLIST
			).order_by("created_at").first()

			if first_in_line:
				first_in_line.status = TournamentRegistration.StatusType.REGISTERED
				first_in_line.save()

				send_telegram.delay(
					telegram_bot_token=settings.TELEGRAM_BOT_TOKEN,
					method=SendMethod.TEXT,
					chat_id=first_in_line.user.telegram_id,
					text=f"♠ Вы в основном составе!"
				)

		# Должно сработать даже если отменят запись те кто в списке ожидания, а не только те кто уже зарегистрированы
		updated_waitlist = TournamentRegistration.objects.filter(
			tournament=tournament,
			status=TournamentRegistration.StatusType.WAITLIST
		).order_by("created_at")

		for position, registration in enumerate(updated_waitlist[:5], start=1):
			if old_position_telegram_ids.get(position) == registration.user.telegram_id:
				continue
			messages = {
				1: "Вы первый в очереди.\nПо сути — уже почти в игре. Будьте на связи.",
				2: "Вы второй номер в резерве.\nЧуть терпения — и вы за столом.",
				3: "Вы в тройке лидеров резерва.\nШансы попасть в турнир сегодня — высокие.",
				4: "Четвёртая позиция в очереди.\nНебольшая дистанция — и вы за столом.",
				5: "Замыкаете топ-5 ожидания.\nИгра ещё может повернуться в вашу сторону."
			}

			message = messages.get(position)
			if message:
				send_telegram.delay(
					telegram_bot_token=settings.TELEGRAM_BOT_TOKEN,
					method=SendMethod.TEXT,
					chat_id=registration.user.telegram_id,
					text=message
				)

	return True, None

@extend_schema(
	tags=["Tournaments"],
	summary="Получить данные о доступных местах",
	responses={
		200: {
			"type": "object",
			"properties": {
				"available_registrations": {"type": "integer"},
				"available_waitlists": {"type": "integer"}
			}
		}
	}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def availability(request, pk):
	"""
	GET /api/tournaments/{id}/availability/
	"""
	tournament = Tournament.objects.filter(pk=pk).first()
	if not tournament:
		return Response({"detail": "Турнир не найден"}, status=404)

	available_registrations = max(tournament.max_participants - tournament.get_participants_count(), 0)
	available_waitlists = max(tournament.max_waitlist - tournament.get_waitlist_count(), 0)

	return Response({"registrations": available_registrations, "waitlists": available_waitlists})

@extend_schema(
	tags=["Tournaments"],
	summary="Проверить регистрацию в турнире",
	responses={
		200: {
			"type": "object",
			"properties": {
				"status": {
					"type": "string",
					"enum": TournamentRegistration.StatusType.values,
					"nullable": True
				},
				"position": {
					"type": "integer"
				}
			}
		},
	}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def registration_status(request, pk):
	"""
	GET /api/tournaments/{id}/registration-status/
	"""
	user = request.user
	tournament = Tournament.objects.filter(pk=pk).first()
	if not tournament:
		return Response({"detail": "Турнир не найден"}, status=404)

	registration = TournamentRegistration.objects.filter(tournament=tournament, user=user).first()

	return Response({
		"status": registration.status if registration else None,
		"waitlist_position": registration.get_waitlist_position() if registration else None
	})

@extend_schema(
	tags=["Tournaments"],
	summary="Регистрация в турнире",
	responses={
		201: TournamentRegistrationSerializer,
		400: {
			"type": "object",
			"properties": {
				"detail": {"type": "string"}
			}
		}
	}
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register(request, pk):
	"""
	POST /api/tournaments/{id}/register/
	"""
	registration, error_response = _perform_registration(pk, request.user)
	if error_response:
		return error_response

	serializer = TournamentRegistrationSerializer(registration, context={"request": request})
	return Response(serializer.data, status=201)

@extend_schema(
	tags=["Tournaments"],
	summary="Регистрация в турнире по telegram_id (для кнопки в рассылке)",
	description="Только для вызова из Telegram-бота с правильным X-Internal-Api-Key",
	responses={
		201: {
			"type": "object",
			"properties": {
				"status": {"type": "string", "enum": TournamentRegistration.StatusType.values}
			}
		},
		400: {
			"type": "object",
			"properties": {
				"detail": {"type": "string"}
			}
		}
	}
)
@api_view(["POST"])
@permission_classes([InternalApiPermission])
def register_internal(request, pk):
	"""
	POST /api/tournaments/{id}/register-internal/
	"""
	telegram_id = request.data.get("telegram_id")
	if not telegram_id:
		return Response({"detail": "telegram_id не передан"}, status=400)

	user = User.objects.filter(telegram_id=telegram_id).first()
	if not user:
		return Response({"detail": "Сначала нужно зарегистрироваться в приложении", "code": "USER_NOT_FOUND"}, status=400)

	registration, error_response = _perform_registration(pk, user)
	if error_response:
		return error_response

	return Response({"status": registration.status}, status=201)

@extend_schema(
	tags=["Tournaments"],
	summary="Отменить регистрацию в турнире",
	responses={
		204: None,
		400: {
			"type": "object",
			"properties": {
				"detail": {"type": "string"}
			}
		}
	}
)
@api_view(["DELETE", "POST"])
@permission_classes([IsAuthenticated])
def unregister(request, pk):
	"""
	DELETE /api/tournaments/{id}/unregister/
	"""
	_, error_response = _perform_unregistration(pk, request.user)
	if error_response:
		return error_response

	return Response(status=204)

@extend_schema(
	tags=["Tournaments"],
	summary="Отмена регистрации в турнире по telegram_id (для кнопки в рассылке)",
	description="Только для вызова из Telegram-бота с правильным X-Internal-Api-Key",
	responses={
		204: None,
		400: {
			"type": "object",
			"properties": {
				"detail": {"type": "string"}
			}
		}
	}
)
@api_view(["POST"])
@permission_classes([InternalApiPermission])
def unregister_internal(request, pk):
	"""
	POST /api/tournaments/{id}/unregister-internal/
	"""
	telegram_id = request.data.get("telegram_id")
	if not telegram_id:
		return Response({"detail": "telegram_id не передан"}, status=400)

	user = User.objects.filter(telegram_id=telegram_id).first()
	if not user:
		return Response({"detail": "Сначала нужно зарегистрироваться в приложении", "code": "USER_NOT_FOUND"}, status=400)

	_, error_response = _perform_unregistration(pk, user)
	if error_response:
		return error_response

	return Response(status=204)
