from pydantic_settings import BaseSettings
from typing import List

class AppSettings(BaseSettings):
	debug: bool
	title: str
	languages: str
	default_language: str
	time_zone: str

	url: str

	domain: str
	host: str
	port: int

	@property
	def languages_list(self) -> List[str]:
		if isinstance(self.languages, str):
			return [i.strip() for i in self.languages.split(",") if i.strip()]
		return []

	class Config:
		env_prefix = "APP_"
		case_sensitive = False
