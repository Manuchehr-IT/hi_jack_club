from aiogram.filters.callback_data import CallbackData

class BaseCallbackData(CallbackData, prefix="base"):
	"""
	role - Роль пользователя (например: user/admin/moder)
	action - Действие (например: menu, back, open, close)
	"""
	role: str
	action: str

class ConfirmCallbackData(BaseCallbackData, prefix="confirm"):
	id: int | str = 0
	method: str

class PageCallbackData(BaseCallbackData, prefix="page"):
	tag: str
	page: int

class ItemCallbackData(BaseCallbackData, prefix="item"):
	tag: str
	id: int
