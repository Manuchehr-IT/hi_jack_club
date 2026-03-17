from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from typing import List

from filters.users import IsAdminFilter
from keyboards.templates import TemplatesInlineKeyboard
from keyboards.spamming import SpammingInlineKeyboard, SpammingReplyKeyboard
from schemes.user import User
from states.admin import StateSpamming
from utils.i18n import i18n
from utils.telegram import MediaProcessing, SafeMessage

router = Router()

@router.message(F.chat.type == "private", StateFilter(StateSpamming.post, StateSpamming.edit_post), F.text == "❌ Отменить", IsAdminFilter())
async def message_cancel(message: Message, state: FSMContext, bot: Bot, user: User):
	current_state = await state.get_state()

	await message.answer(text=i18n.translate(namespace="responses.base", key="action_cancelled.message", lang=user.language_code), reply_markup=ReplyKeyboardRemove())

	if current_state == StateSpamming.post:
		await state.clear()
		await message.answer(
			text=i18n.translate(namespace="commands.admin", key="message", lang=user.language_code),
			reply_markup=TemplatesInlineKeyboard.admin_menu()
		)
	else:
		await state.set_state(StateSpamming.settings)
		await message.answer(
			text=i18n.translate(namespace="responses.spamming", key="preview.message", lang=user.language_code),
			reply_markup=SpammingInlineKeyboard.settings()
		)

@router.message(F.chat.type == "private", F.text | F.caption | F.photo | F.video, StateFilter(StateSpamming.post, StateSpamming.edit_post), IsAdminFilter())
async def message_post(message: Message, state: FSMContext, bot: Bot, user: User, album: List[Message] | None = None):
	spamming_locale = i18n.translate(namespace="responses.spamming", lang=user.language_code)
	album = album or [message]
	msg_text = message.html_text

	if msg_text and len(message.text or message.caption) > 1000:
		return await message.answer(
			text=spamming_locale["errors"]["length_limit"]["message"],
			reply_markup=SpammingReplyKeyboard.cancel()
		)

	if message.photo or message.video:
		media_json = MediaProcessing.parse_media_messages(messages=album)
		await state.update_data(text=msg_text, media_json=media_json)
	else:
		await state.update_data(text=msg_text, media_json=None)

	await state.set_state(StateSpamming.settings)

	msg = await message.answer(text="...", reply_markup=ReplyKeyboardRemove())
	await SafeMessage.message_delete(message=msg)

	await message.answer(
		text=spamming_locale["preview"]["message"],
		reply_markup=SpammingInlineKeyboard.settings()
	)