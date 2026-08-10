from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from keyboards.tournament import TournamentInlineKeyboard, TournamentRegisterCallbackData
from schemes.user import User
from services.tournament import TournamentService
from utils.i18n import i18n

router = Router()

def _parse_response(response) -> dict:
	try:
		return response.json()
	except ValueError:
		return {}

async def _switch_markup(call: CallbackQuery, markup: InlineKeyboardMarkup) -> None:
	try:
		await call.message.edit_reply_markup(reply_markup=markup)
	except TelegramBadRequest:
		pass

@router.callback_query(F.message.chat.type == "private", TournamentRegisterCallbackData.filter(F.action == "register"))
async def handle_tournament_register(call: CallbackQuery, callback_data: TournamentRegisterCallbackData, user: User):
	tournament_locale = i18n.translate(namespace="responses.tournament", lang=user.language_code)

	response = await TournamentService.register(
		tournament_id=callback_data.tournament_id,
		telegram_id=call.from_user.id
	)
	data = _parse_response(response)

	if response.status_code == 201:
		text = (
			tournament_locale["register"]["success"]["waitlist"]
			if data.get("status") == "WAITLIST"
			else tournament_locale["register"]["success"]["registered"]
		)
		await _switch_markup(call, TournamentInlineKeyboard.unregister(callback_data.tournament_id))
		return await call.answer(text=text, show_alert=True)

	# Пользователь уже записан (например, кнопка не успела обновиться после прошлого нажатия) — приводим её в актуальное состояние
	if data.get("code") == "ALREADY_REGISTERED":
		await _switch_markup(call, TournamentInlineKeyboard.unregister(callback_data.tournament_id))

	await call.answer(text=data.get("detail") or tournament_locale["register"]["error"]["unavailable"], show_alert=True)

@router.callback_query(F.message.chat.type == "private", TournamentRegisterCallbackData.filter(F.action == "unregister"))
async def handle_tournament_unregister(call: CallbackQuery, callback_data: TournamentRegisterCallbackData, user: User):
	tournament_locale = i18n.translate(namespace="responses.tournament", lang=user.language_code)

	response = await TournamentService.unregister(
		tournament_id=callback_data.tournament_id,
		telegram_id=call.from_user.id
	)

	if response.status_code == 204:
		await _switch_markup(call, TournamentInlineKeyboard.register(callback_data.tournament_id))
		return await call.answer(text=tournament_locale["unregister"]["success"], show_alert=True)

	data = _parse_response(response)

	# Пользователь и так не записан (например, кнопка не успела обновиться) — приводим её в актуальное состояние
	if data.get("code") == "NOT_REGISTERED":
		await _switch_markup(call, TournamentInlineKeyboard.register(callback_data.tournament_id))

	await call.answer(text=data.get("detail") or tournament_locale["register"]["error"]["unavailable"], show_alert=True)
