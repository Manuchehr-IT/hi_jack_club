# app/core/container.py
from aiogram import Bot

class Container:
	bot: Bot | None = None

container = Container()
