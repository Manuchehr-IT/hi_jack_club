from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo

from keyboards import BaseCallbackData

class TemplatesInlineKeyboard:
	@staticmethod
	def main_menu(web_app_url: str):
		builder = InlineKeyboardBuilder()
		builder.button(text="Открыть", web_app=WebAppInfo(url=web_app_url))
		builder.adjust(1)
		return builder.as_markup()

	@staticmethod
	def admin_menu():
		builder = InlineKeyboardBuilder()
		builder.button(text="Рассылка", callback_data=BaseCallbackData(role="admin", action="spamming"))
		builder.adjust(1)
		return builder.as_markup()