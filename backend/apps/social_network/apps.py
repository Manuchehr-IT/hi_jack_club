from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError

class SocialNetworkConfig(AppConfig):
	default_auto_field = "django.db.models.BigAutoField"
	name = "apps.social_network"

	def ready(self):
		from .models import SocialNetwork

		def create_default_links(sender, **kwargs):
			try:
				if sender.name == self.name:
					defaults = {
						"map": "https://yandex.ru/maps/org/khay_dzhek_klab_/83743013847?si=hkgyga7pje6fw6n1znjpxqhjk0",
						"ig": "https://www.instagram.com/hi_jack_club",
						"vk": "https://vk.com/hijackclub",
						"tg": "https://t.me/telegram/",
						"vk_broadcast": "https://vk.com/hijackclub",
						"vk_broadcast_archive": "https://vk.com/hijackclub",
					}
					for social_type, url in defaults.items():
						SocialNetwork.objects.get_or_create(social_type=social_type, defaults={"url": url})
			except OperationalError:
				pass

		post_migrate.connect(create_default_links, sender=self)
