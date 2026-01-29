from aiogram.utils.keyboard import ReplyKeyboardBuilder

class TemplatesReplyKeyboard:
	@staticmethod
	def main_menu(access: str):
		builder = ReplyKeyboardBuilder()

		builder.button(text="Test")

		builder.adjust(1)
		return builder.as_markup(resize_keyboard=True)
