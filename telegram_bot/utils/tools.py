from datetime import datetime, timezone, timedelta

def is_valid_date_time(date_str: str) -> bool | datetime:
	"""
	Проверяет, соответствует ли строка формату 'чч:мм дд.мм.гггг'.

	:param date_str: Строка с датой и временем.
	:return: True, если строка соответствует формату, иначе False.
	"""
	date_format = "%H:%M %d.%m.%Y"  # Формат для проверки
	try:
		return datetime.strptime(date_str, date_format)  # Преобразуем строку в объект datetime
	except ValueError as e:
		return False
