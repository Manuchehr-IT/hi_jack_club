from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards import BaseCallbackData

class SpammingCallbackData(BaseCallbackData, prefix="spamming"):
	...

class SpammingInlineKeyboard:
	@staticmethod
	def settings():
		builder = InlineKeyboardBuilder()
		builder.button(text="👁 Предпросмотр", callback_data=SpammingCallbackData(role="admin", action="preview"))
		builder.button(text="📝 Изменить сообщение", callback_data=SpammingCallbackData(role="admin", action="edit_post"))
		builder.button(text="▶️ Запустить", callback_data=SpammingCallbackData(role="admin", action="run"))
		builder.adjust(1, 2)
		return builder.as_markup()
