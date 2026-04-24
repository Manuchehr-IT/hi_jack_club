from pydantic_settings import BaseSettings
from typing import List

class TelegramBotSettings(BaseSettings):
	token: str
	admin_ids: str

	@property
	def admin_ids_list(self) -> List[int]:
		if isinstance(self.admin_ids, str):
			return [int(i.strip()) for i in self.admin_ids.split(",") if i.strip()]
		return []

	class Config:
		env_prefix = "TELEGRAM_BOT_"
		case_sensitive = False
