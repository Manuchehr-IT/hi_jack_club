import json
import uuid
from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from celery_app.tasks.telegram import send_telegram, broadcast_messages
from celery_app.tasks.telegram.schemas import SendMethod
from core.config import settings
from filters.users import IsAdminFilter
# from infrastructure.redis import redis
from keyboards import BaseCallbackData
from keyboards.spamming import SpammingCallbackData, SpammingReplyKeyboard
from services.user import UserService
from schemes.user import User
from states.admin import StateSpamming
from utils.i18n import i18n
from utils.telegram import SafeMessage

router = Router()

@router.callback_query(F.message.chat.type == "private", BaseCallbackData.filter((F.role == "admin") & (F.action == "spamming")), IsAdminFilter())
async def handle_spamming(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)
	await state.set_state(StateSpamming.post)
	await call.message.answer(
		text=i18n.translate(namespace="responses.spamming", key="message", lang=user.language_code),
		reply_markup=SpammingReplyKeyboard.cancel()
	)

@router.callback_query(
	F.message.chat.type == "private",
	SpammingCallbackData.filter((F.role == "admin") & (F.action == "preview")),
	StateSpamming.settings,
	IsAdminFilter()
)
async def handle_preview(call: CallbackQuery, callback_data: SpammingCallbackData, state: FSMContext, bot: Bot, user: User):
	data_state = await state.get_data()

	await call.answer()

	if data_state.get("media_json"):
		method = SendMethod.MEDIA_GROUP
		payload = {"media": json.dumps(data_state["media_json"])}
	else:
		method = SendMethod.TEXT
		payload = {"text": data_state["text"]}

	send_telegram.delay(
		telegram_bot_token=settings.telegram_bot.token,
		method=method,
		chat_id=user.id,
		**payload
	)

@router.callback_query(
	F.message.chat.type == "private",
	SpammingCallbackData.filter((F.role == "admin") & (F.action == "edit_post")),
	StateSpamming.settings,
	IsAdminFilter()
)
async def handle_edit_post(call: CallbackQuery, callback_data: SpammingCallbackData, state: FSMContext, bot: Bot, user: User):
	await SafeMessage.message_delete(message=call.message)
	await state.set_state(StateSpamming.edit_post)
	await call.message.answer(
		text=i18n.translate(namespace="responses.spamming", key="editing.message", lang=user.language_code),
		reply_markup=SpammingReplyKeyboard.cancel()
	)

@router.callback_query(
	F.message.chat.type == "private",
	SpammingCallbackData.filter((F.role == "admin") & (F.action == "run")),
	StateSpamming.settings,
	IsAdminFilter()
)
async def handle_run(call: CallbackQuery, callback_data: SpammingCallbackData, state: FSMContext, bot: Bot, user: User):
	spamming_locale = i18n.translate(namespace="responses.spamming", lang=user.language_code)

	# is_running = await redis.set("spamming_is_running", "1", nx=True)
	# if not is_running:
	# 	text = spamming_locale["errors"]["spamming_is_running"]["message"]
	# 	return await call.answer(text=text, show_alert=True)

	data_state = await state.get_data()
	if data_state.get("media_json"):
		method = SendMethod.MEDIA_GROUP
		payload = {"media": json.dumps(data_state["media_json"])}
	else:
		method = SendMethod.TEXT
		payload = {"text": data_state["text"]}


	user_ids = await UserService.get_user_ids()
	total_users = len(user_ids)
	spamming_id = str(uuid.uuid4())

	text = spamming_locale["run"]["message"].format(
		total_users=total_users,
		spamming_id=spamming_id
	)

	await SafeMessage.message_delete(message=call.message)
	await call.message.answer(text=text)

	await state.clear()

	# await redis.hset(f"spamming_id:{spamming_id}", mapping={
	# 	"total": total_users,
	# 	"processed": 0,
	# 	"successful": 0,
	# 	"failed": 0
	# })

	broadcast_messages.delay(
		telegram_bot_token=settings.telegram_bot.token,
		method=method,
		chat_ids=user_ids,
		**payload
	)

	# for u in users:
	# 	send_telegram.delay(spamming_id=spamming_id, user_id=u.id, content_type=content_type, **payload)
