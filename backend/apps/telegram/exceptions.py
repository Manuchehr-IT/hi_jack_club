from rest_framework.exceptions import APIException

class TelegramAuthError(APIException):
	"""Базовое исключение для ошибок Telegram аутентификации"""
	status_code = 401
	default_detail = "Telegram authentication error"
	default_code = "telegram_auth_error"

class InvalidTelegramDataError(TelegramAuthError):
	"""Невалидные данные от Telegram"""
	default_detail = "Invalid Telegram initData"
	default_code = "invalid_telegram_data"

	def __init__(self, detail=None):
		if detail is None:
			detail = self.default_detail
		super().__init__(detail)

class ExpiredTelegramDataError(TelegramAuthError):
	"""Данные Telegram устарели"""
	default_detail = "Telegram initData has expired"
	default_code = "expired_telegram_data"

	def __init__(self, detail=None):
		if detail is None:
			detail = self.default_detail
		super().__init__(detail)
