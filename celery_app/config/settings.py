# pyright: reportCallIssue=false

from pydantic_settings import BaseSettings
from typing import Literal

from .schemas import CelerySettings

class Settings(BaseSettings):
	environment: Literal["development", "staging", "production"]

	celery: CelerySettings = CelerySettings()

	class Config:
		extra = "ignore"
		env_file = [".env"]
		env_file_encoding = "utf-8"

settings = Settings()
