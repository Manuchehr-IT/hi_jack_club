import asyncio
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Any, Awaitable, Callable, Dict

class AlbumMiddleware(BaseMiddleware):
	def __init__(self, latency: float = 1):
		super().__init__()
		self.latency = latency
		self.album_data: Dict[str, list[Message]] = {}
		self.tasks: Dict[str, asyncio.Task] = {}

	async def __call__(
		self,
		handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
		event: Message,
		data: Dict[str, Any]
	) -> Any:
		if isinstance(event, Message) and event.media_group_id:
			await self._process_message(event, handler, data)
			return
		return await handler(event, data)

	async def _process_message(self, message: Message, handler, data: dict):
		group_id = message.media_group_id

		if group_id not in self.album_data:
			self.album_data[group_id] = []

		self.album_data[group_id].append(message)

		if group_id in self.tasks:
			self.tasks[group_id].cancel()

		self.tasks[group_id] = asyncio.create_task(
			self._delayed_process_album(group_id, handler, data)
		)

	async def _delayed_process_album(self, group_id: str, handler, data: dict):
		try:
			await asyncio.sleep(self.latency)
			await self._process_album(group_id, handler, data)
		except asyncio.CancelledError:
			pass  # Игнорируем отменённые задачи


	async def _process_album(self, group_id: str, handler, data: dict):
		album = self.album_data.pop(group_id, [])
		print(f"Обработка альбома {group_id} с {len(album)} сообщениями.")

		if not album:
			return

		album.sort(key=lambda m: m.message_id)
		data = data.copy()
		data["album"] = album
		message = album[0]

		try:
			await handler(message, data)
		finally:
			self.tasks.pop(group_id, None)
