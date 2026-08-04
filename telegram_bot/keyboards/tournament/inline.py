from keyboards import BaseCallbackData

class TournamentRegisterCallbackData(BaseCallbackData, prefix="tournament"):
	tournament_id: int

class TournamentInlineKeyboard:
	@staticmethod
	def register_markup(tournament_id: int) -> dict:
		"""Разметка кнопки быстрой регистрации для рассылки (передаётся в Celery как JSON)."""
		return {
			"inline_keyboard": [[{
				"text": "♠ Записаться на турнир",
				"callback_data": TournamentRegisterCallbackData(
					role="user", action="register", tournament_id=tournament_id
				).pack()
			}]]
		}
