from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from typing import Tuple

# from celery_app.tasks.telegram import send_message
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_ADMIN_IDS
from apps.telegram.schemas import TelegramUser
from apps.telegram.utils import save_avatar

User = get_user_model()

class UserService:
	def get_or_create_from_telegram(self, tg_user: TelegramUser) -> Tuple[User, bool]:
		telegram_id = tg_user.id

		try:
			user = User.objects.get(telegram_id=telegram_id)
			user.first_name = tg_user.first_name
			user.username = tg_user.username
			user.language_code = tg_user.language_code
			user.save()

			created = False

		except User.DoesNotExist as e:
			if str(telegram_id) in TELEGRAM_BOT_ADMIN_IDS:
				password = get_random_string(12)

				user = User.objects.create_superuser(
					telegram_id=telegram_id,
					first_name=tg_user.first_name,
					username=tg_user.username,
					language_code=tg_user.language_code,
					password=password
				)

				send_message.delay(
					telegram_bot_token=TELEGRAM_BOT_TOKEN,
					chat_id=telegram_id,
					text=f"<b>Данные для входа в админку:</b>\n<b>login:</b> {telegram_id}\n<b>password:</b> {password}"
				)
			else:
				user = User.objects.create_user(
					telegram_id=telegram_id,
					first_name=tg_user.first_name,
					username=tg_user.username,
					language_code=tg_user.language_code,
				)

			created = True

		save_avatar(user, tg_user.photo_url)

		return user, created
