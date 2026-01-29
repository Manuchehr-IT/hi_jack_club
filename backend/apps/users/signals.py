# # apps/users/signals.py
# from django.db.models.signals import post_save, pre_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User

# from celery_app.tasks.send_notification import send_notification

# @receiver(post_save, sender=User)
# def on_password_change(sender, instance, created: bool, **kwargs):
# 	if created and "password" in kwargs:
# 		send_notification.delay(
# 			user_id=instance.user_id, #instance - это ведь User объект?
# 			text=f"<b>Данные для входа в админку:</b>\n<b>login:</b> {instance.user_id}\n<b>password:</b> {kwargs['password']}"
# 		)
