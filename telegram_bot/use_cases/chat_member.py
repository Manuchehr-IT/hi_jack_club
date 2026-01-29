from aiogram import Bot, exceptions

from infrastructure.logger import logger

async def get_chat_member(bot: Bot, chat_id: int, user_id: int):
	try:
		return await bot.get_chat_member(chat_id, user_id)
	except exceptions.TelegramBadRequest as e:
		if "chat not found" in str(e).lower():
			logger.error("Чат/канал не найден")
		else:
			logger.error(f"Другая ошибка TelegramBadRequest: {e}")

	except exceptions.TelegramForbiddenError as e:
		if "bot was kicked" in str(e).lower():
			logger.error("Бот заблокирован в чате/канале")
		elif "bot is not a member" in str(e).lower():
			logger.error("Бот не находится в группе/канале")
		else:
			logger.error(f"Другая ошибка TelegramForbiddenError: {e}")

async def kick_chat_member(bot: Bot, chat_id: int, user_id: int) -> bool:
	try:
		await bot.ban_chat_member(chat_id, user_id)
		await bot.unban_chat_member(chat_id, user_id)
		return True
	except Exception as e:
		logger.error(f"Ошибка исключения пользователя из группы: {e}")
		return False
