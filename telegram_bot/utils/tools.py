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

def format_date(date_utc: datetime): # 2025-07-25 13:11:26.998099+00:00
	# Московское время (UTC+3)
	msk_timezone = timezone(timedelta(hours=3))
	date_at_msk = date_utc.astimezone(msk_timezone)

	# Формат: DD-MM-YYYY HH:MM
	formatted_date = date_at_msk.strftime("%d/%m/%Y %H:%M")

	return formatted_date
