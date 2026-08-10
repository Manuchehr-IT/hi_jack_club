from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards import BaseCallbackData

class TournamentRegisterCallbackData(BaseCallbackData, prefix="tournament"):
	tournament_id: int

REGISTER_BUTTON_TEXT = "♠ Записаться на турнир"
UNREGISTER_BUTTON_TEXT = "✖ Отписаться от турнира"

class TournamentInlineKeyboard:
	@staticmethod
	def register(tournament_id: int) -> InlineKeyboardMarkup:
		builder = InlineKeyboardBuilder()
		builder.button(
			text=REGISTER_BUTTON_TEXT,
			callback_data=TournamentRegisterCallbackData(role="user", action="register", tournament_id=tournament_id)
		)
		return builder.as_markup()

	@staticmethod
	def unregister(tournament_id: int) -> InlineKeyboardMarkup:
		builder = InlineKeyboardBuilder()
		builder.button(
			text=UNREGISTER_BUTTON_TEXT,
			callback_data=TournamentRegisterCallbackData(role="user", action="unregister", tournament_id=tournament_id)
		)
		return builder.as_markup()

	@staticmethod
	def register_markup(tournament_id: int) -> dict:
		"""Разметка кнопки быстрой регистрации для рассылки (передаётся в Celery как JSON)."""
		return TournamentInlineKeyboard.register(tournament_id).model_dump(mode="json", exclude_none=True)
