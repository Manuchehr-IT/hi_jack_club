from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Any, Awaitable, Callable, Dict

from infrastructure.redis import redis
from utils.i18n import i18n

class ThrottlingMiddleware(BaseMiddleware):
	def __init__(self) -> None:
		super().__init__()

	async def __call__(
		self,
		handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
		event: TelegramObject,
		data: Dict[str, Any]
	) -> Any:
		event_out = event
		if isinstance(event, list):
			event = event[0]

		user_id = event.from_user.id
		user_key = f"user{user_id}"

		user_data = await redis.get(user_key)

		if user_data:
			if int(user_data.decode()) == 1:
				lang = data["user"].language_code
				text_json = i18n.translate(namespace="responses.throttling", lang=lang)

				await redis.set(user_key, value=0, px=100)

				if isinstance(event, CallbackQuery):
					return await event.answer(text_json["callback"], show_alert=True)
				return await event.answer(text_json["message"])
			return

		await redis.set(user_key, value=1, px=100)
		return await handler(event_out, data)
