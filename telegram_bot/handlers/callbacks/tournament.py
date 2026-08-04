from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.tournament import TournamentRegisterCallbackData
from schemes.user import User
from services.tournament import TournamentService
from utils.i18n import i18n

router = Router()

@router.callback_query(F.message.chat.type == "private", TournamentRegisterCallbackData.filter())
async def handle_tournament_register(call: CallbackQuery, callback_data: TournamentRegisterCallbackData, user: User):
	tournament_locale = i18n.translate(namespace="responses.tournament", lang=user.language_code)

	response = await TournamentService.register(
		tournament_id=callback_data.tournament_id,
		telegram_id=call.from_user.id
	)

	if response.status_code == 201:
		registration_status = response.json().get("status")
		text = (
			tournament_locale["register"]["success"]["waitlist"]
			if registration_status == "WAITLIST"
			else tournament_locale["register"]["success"]["registered"]
		)
		return await call.answer(text=text, show_alert=True)

	try:
		detail = response.json().get("detail")
	except ValueError:
		detail = None

	await call.answer(text=detail or tournament_locale["register"]["error"]["unavailable"], show_alert=True)
