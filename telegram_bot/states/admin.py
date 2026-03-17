from aiogram.fsm.state import State, StatesGroup

class StateSpamming(StatesGroup):
	post = State()
	settings = State()
	edit_post = State()
