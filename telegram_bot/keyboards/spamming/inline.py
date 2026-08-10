from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards import BaseCallbackData

class SpammingCallbackData(BaseCallbackData, prefix="spamming"):
	...

class SpammingInlineKeyboard:
	@staticmethod
	def settings(tournament_title: str | None = None):
		if tournament_title:
			display_title = tournament_title if len(tournament_title) <= 30 else f"{tournament_title[:30]}…"
			tournament_button_text = f"🎟 {display_title}"
		else:
			tournament_button_text = "🎟 Кнопка турнира"

		builder = InlineKeyboardBuilder()
		builder.button(text="👁 Предпросмотр", callback_data=SpammingCallbackData(role="admin", action="preview"))
		builder.button(text="📝 Изменить сообщение", callback_data=SpammingCallbackData(role="admin", action="edit_post"))
		builder.button(text=tournament_button_text, callback_data=SpammingCallbackData(role="admin", action="attach_tournament"))
		builder.button(text="▶️ Запустить", callback_data=SpammingCallbackData(role="admin", action="run"))
		builder.adjust(1, 2, 1)
		return builder.as_markup()
