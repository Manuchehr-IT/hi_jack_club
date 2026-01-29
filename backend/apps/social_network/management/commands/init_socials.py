from django.apps import apps
from django.core.management.base import BaseCommand

class Command(BaseCommand):
	help = 'Создает начальные записи для социальных сетей'

	def handle(self, *args, **kwargs):
		SocialNetwork = apps.get_model('social_network', 'SocialNetwork')

		socials = [
			('map', 'Карта', ''),
			('tg', 'Telegram', 'https://t.me/your_channel'),
			('vk', 'ВКонтакте', 'https://vk.com/your_group'),
			('ig', 'Instagram', 'https://instagram.com/your_profile'),
			('vk_broadcast', 'VK Трансляции', ''),
			('vk_broadcast_archive', 'Архив VK Трансляций', ''),
		]

		for social_type, title, url in socials:
			SocialNetwork.objects.get_or_create(
				social_type=social_type,
				defaults={'url': url}
			)

		self.stdout.write(self.style.SUCCESS('Соцсети созданы!'))
