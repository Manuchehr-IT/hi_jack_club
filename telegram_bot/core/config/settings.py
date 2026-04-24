# pyright: reportCallIssue=false

from pydantic_settings import BaseSettings
from typing import Literal

from .schemas import AppSettings, CelerySettings, LoggerSettings, RedisSettings, TelegramBotSettings

class Settings(BaseSettings):
	environment: Literal["development", "staging", "production"]
	secret_key: str
	proxy: str

	app: AppSettings = AppSettings()
	celery: CelerySettings = CelerySettings()
	logger: LoggerSettings = LoggerSettings()
	redis: RedisSettings = RedisSettings()
	telegram_bot: TelegramBotSettings = TelegramBotSettings()

	class Config:
		extra = "ignore"
		env_file = [".env"]
		env_file_encoding = "utf-8"

settings = Settings()
