from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram.fsm.context import FSMContext

from core.config import settings

class IsAdminFilter(Filter):
	async def __call__(self, message: Message) -> bool:
		return message.from_user.id in settings.telegram_bot.admin_ids_list
		# user = await UserRepository.get_by_id(user_id=message.from_user.id)
		# if not user:
		# 	return False
		# return user.is_admin

# class IsBlockFilter(Filter):
# 	async def __call__(self, message: Message) -> bool:
# 		user = await UserRepository.get_by_id(user_id=message.from_user.id)
# 		if not user:
# 			return False
# 		return user.is_block
