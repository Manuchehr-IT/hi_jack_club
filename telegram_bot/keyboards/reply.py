from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def custom_markup(*args, adjust: tuple = (1,)) -> ReplyKeyboardMarkup:
	builder = ReplyKeyboardBuilder()

	for text in args: builder.button(text=text)

	builder.adjust(*adjust)
	return builder.as_markup(resize_keyboard=True)
