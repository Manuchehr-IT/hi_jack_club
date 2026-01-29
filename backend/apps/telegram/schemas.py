from pydantic import BaseModel
from typing import Any, Dict

class TelegramUser(BaseModel):
	"""Объект пользователя Telegram WebApp"""
	id: int
	is_bot: bool = False
	first_name: str | None = None
	last_name: str | None = None  
	username: str | None = None
	language_code: str | None = None
	allows_write_to_pm: bool | None = None
	is_premium: bool = False
	photo_url: str | None = None

class TelegramChat(BaseModel):
	"""Объект чата Telegram WebApp"""
	id: int
	type: str | None = None
	title: str | None = None

class TelegramInitData(BaseModel):
	"""Объект init_data Telegram WebApp"""
	query_id: str | None = None
	auth_date: int | None = None
	hash: str | None = None
	start_param: str | None = None
	user: TelegramUser | None = None
	chat: TelegramChat | None = None
	other_fields: Dict[str, Any] = {}
