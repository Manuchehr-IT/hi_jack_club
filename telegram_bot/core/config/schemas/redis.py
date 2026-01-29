from pydantic import RedisDsn, computed_field
from pydantic_settings import BaseSettings

class RedisSettings(BaseSettings):
	host: str
	port: int
	db: int
	username: str | None = None
	password: str | None = None

	@computed_field
	@property
	def dsn(self) -> RedisDsn:
		return RedisDsn.build(
			scheme="redis",
			host=self.host,
			port=self.port,
			path=str(self.db),
			username=self.username,
			password=self.password
		)

	class Config:
		env_prefix = "REDIS_"
		case_sensitive = False
