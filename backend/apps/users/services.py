from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from typing import Tuple

from apps.telegram.schemas import TelegramUser
from apps.telegram.utils import save_avatar
from celery_app.tasks.telegram import send_telegram
from celery_app.tasks.telegram.schemas import SendMethod

User = get_user_model()

class UserService:
	def get_or_create_from_telegram(self, tg_user: TelegramUser, referral_code: str | None) -> Tuple[User, bool]:
		telegram_id = tg_user.id

		try:
			user = User.objects.get(telegram_id=telegram_id)
			user.first_name = tg_user.first_name
			user.username = tg_user.username
			user.language_code = tg_user.language_code
			user.save()

			created = False

		except User.DoesNotExist as e:
			referrer = None
			if referral_code:
				referrer = User.objects.filter(referral_code=referral_code).first()

			if str(telegram_id) in settings.TELEGRAM_BOT_ADMIN_IDS:
				password = get_random_string(12)

				user = User.objects.create_superuser(
					referrer=referrer,
					telegram_id=telegram_id,
					first_name=tg_user.first_name,
					username=tg_user.username,
					language_code=tg_user.language_code,
					password=password,
				)

				send_telegram.delay(
					telegram_bot_token=settings.TELEGRAM_BOT_TOKEN,
					method=SendMethod.TEXT,
					chat_id=telegram_id,
					text=f"<b>Данные для входа в админку:</b>\n<b>login:</b> {telegram_id}\n<b>password:</b> {password}"
				)
			else:
				user = User.objects.create_user(
					referrer=referrer,
					telegram_id=telegram_id,
					first_name=tg_user.first_name,
					username=tg_user.username,
					language_code=tg_user.language_code,
				)

			created = True

		save_avatar(user, tg_user.photo_url)

		return user, created
