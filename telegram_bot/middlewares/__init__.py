from aiogram import Dispatcher
from .user import UserMiddleware
from .album import AlbumMiddleware
from .throttling import ThrottlingMiddleware

def register_middlewares(dp: Dispatcher):
	dp.message.middleware(UserMiddleware(enable_create_user=False))
	# dp.message.middleware(AlbumMiddleware())
	dp.message.middleware(ThrottlingMiddleware())

	dp.callback_query.middleware(UserMiddleware(enable_create_user=False))
	dp.callback_query.middleware(ThrottlingMiddleware())
