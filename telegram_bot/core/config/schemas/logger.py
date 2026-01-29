from pydantic_settings import BaseSettings

class LoggerSettings(BaseSettings):
	level: str
	format: str

	file: str
	max_size: int
	backup_count: int

	class Config:
		env_prefix = "LOGGER_"
		case_sensitive = False
