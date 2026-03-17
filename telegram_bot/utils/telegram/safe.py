import logging
from aiogram import Bot
from aiogram.types import Chat, Message, InlineKeyboardMarkup

logger = logging.getLogger()

class SafeMessage:
	"""Утилита для безопасного вызова методов Message, предотвращает исключения"""
	@staticmethod
	async def message_delete(message: Message) -> bool:
		try:
			return await message.delete()
		except Exception as e:
			logger.error("Ошибка при вызове `delete`: %s", e)
			return False

	@staticmethod
	async def message_edit_reply_markup(message: Message, reply_markup: InlineKeyboardMarkup | None = None) -> Message | bool | None:
		try:
			return await message.edit_reply_markup(reply_markup=reply_markup)
		except Exception as e:
			logger.error("Ошибка при вызове `edit_reply_markup`: %s", e)

	@staticmethod
	async def message_edit_text(message: Message, text: str, **kwargs) -> Message | bool | None:
		try:
			return await message.edit_text(text=text, **kwargs)
		except Exception as e:
			logger.error("Ошибка при вызове `edit_text`: %s", e)

	@staticmethod
	async def message_reply(message: Message, text: str, **kwargs) -> Message:
		try:
			return await message.reply(text=text, **kwargs)
		except:
			return await message.answer(text=text, **kwargs)

	@staticmethod
	async def get_chat(bot: Bot, chat_id: int | str) -> Chat | None:
		try:
			return await bot.get_chat(chat_id)
		except Exception as e:
			logger.error("Ошибка при вызове `get_chat`: %s", e)

	@staticmethod
	async def send_message(bot: Bot, chat_id: int | str, text: str, **kwargs) -> Message | None:
		try:
			return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
		except Exception as e:
			logger.error("Ошибка при вызове `send_message`: %s", e)
