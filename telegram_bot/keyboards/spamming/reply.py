from aiogram.utils.keyboard import ReplyKeyboardBuilder

class SpammingReplyKeyboard:
	@staticmethod
	def cancel():
		builder = ReplyKeyboardBuilder()
		builder.button(text="❌ Отменить")
		builder.adjust(1)
		return builder.as_markup(resize_keyboard=True)
