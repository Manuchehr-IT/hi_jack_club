# Конфигурация для logging.config.dictConfig
LOGGING_CONFIG = {
	"version": 1,
	"disable_existing_loggers": False,
	"formatters": {
		"standard": {
			"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
			"datefmt": "%Y-%m-%d %H:%M:%S",
		},
		"detailed": {
			"format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
			"datefmt": "%Y-%m-%d %H:%M:%S",
		},
	},
	"handlers": {
		"console": {
			"class": "logging.StreamHandler",
			"level": "INFO",
			"formatter": "standard",
			"stream": "ext://sys.stdout",
		},
		"file": {
			"class": "logging.handlers.RotatingFileHandler",
			"level": "INFO",
			"formatter": "detailed",
			"filename": "logs/app.log",
			"maxBytes": 10 * 1024 * 1024,
			"backupCount": 5,
			"encoding": "utf8",
		},
	},
	"root": {
		"handlers": ["console", "file"],
		"level": "INFO",
	},
}