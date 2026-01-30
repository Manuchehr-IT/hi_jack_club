from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
	domain: str

	@property
	def api_url(self):
		return f"https://{self.domain}/api"

	class Config:
		env_prefix = "APP_"
		case_sensitive = False
