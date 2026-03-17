from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
	api_url: str

	class Config:
		env_prefix = "APP_"
		case_sensitive = False
