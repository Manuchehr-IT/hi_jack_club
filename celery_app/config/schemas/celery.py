from pydantic_settings import BaseSettings

class CelerySettings(BaseSettings):
	broker_url: str

	class Config:
		env_prefix = "CELERY_"
		case_sensitive = False
