from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters.users import IsAdminFilter
from keyboards.templates import TemplatesInlineKeyboard
from schemes.user import User
from utils.i18n import i18n

router = Router()

@router.message(Command("admin"), F.chat.type == "private", IsAdminFilter())
async def command_admin_private(message: Message, state: FSMContext, bot: Bot, user: User):
	await state.clear()

	text = i18n.translate(namespace="commands.admin", key="message", lang=user.language_code)

	await message.answer(
		text=text,
		reply_markup=TemplatesInlineKeyboard.admin_menu()
	)
