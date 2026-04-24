# pyright: reportCallIssue=false

from pydantic_settings import BaseSettings
from typing import Literal

from .schemas import AppSettings, CelerySettings

class Settings(BaseSettings):
	environment: Literal["development", "staging", "production"]
	secret_key: str
	proxy: str

	app: AppSettings = AppSettings()
	celery: CelerySettings = CelerySettings()

	class Config:
		extra = "ignore"
		env_file = [".env"]
		env_file_encoding = "utf-8"

settings = Settings()
