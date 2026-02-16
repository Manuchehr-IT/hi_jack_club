from rest_framework.exceptions import APIException

class CustomValidationError(APIException):
	"""Универсальная ошибка валидации с кастомным форматом"""

	def __init__(self, code: str, message: str, status_code: int = 400, **kwargs):
		self.status_code = status_code
		self.detail = {
			"code": code,
			"message": message,
			# **kwargs,
		}
