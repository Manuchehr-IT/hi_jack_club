# from aiogram.filters import Filter
# from aiogram.types import CallbackQuery, Message, TelegramObject
# from aiogram.fsm.context import FSMContext

# from repositories.user import UserRepository

# class IsAdminFilter(Filter):
# 	async def __call__(self, message: Message) -> bool:
# 		user = await UserRepository.get_by_id(user_id=message.from_user.id)
# 		if not user:
# 			return False
# 		return user.is_admin

# class IsBlockFilter(Filter):
# 	async def __call__(self, message: Message) -> bool:
# 		user = await UserRepository.get_by_id(user_id=message.from_user.id)
# 		if not user:
# 			return False
# 		return user.is_block
