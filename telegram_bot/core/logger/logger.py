import logging.config

from core.config import settings
from .config import LOGGING_CONFIG

def setup_logging() -> None:
	LOGGING_CONFIG["handlers"]["file"]["filename"] = settings.logger.file
	LOGGING_CONFIG["handlers"]["file"]["maxBytes"] = settings.logger.max_size * 1024 * 1024
	LOGGING_CONFIG["handlers"]["file"]["backupCount"] = settings.logger.backup_count
	LOGGING_CONFIG["root"]["level"] = settings.logger.level

	logging.config.dictConfig(LOGGING_CONFIG)
