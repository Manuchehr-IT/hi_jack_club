from django.db import models

class SocialNetwork(models.Model):
	class SocialType(models.TextChoices):
		MAP = 'map', 'Карта (Map)'
		TELEGRAM = 'tg', 'Telegram'
		VK = 'vk', 'ВКонтакте'
		INSTAGRAM = 'ig', 'Instagram'
		VK_BROADCAST = 'vk_broadcast', 'VK Трансляции'
		VK_BROADCAST_ARCHIVE = 'vk_broadcast_archive', 'Архив VK Трансляций'

	social_type = models.CharField(max_length=30, choices=SocialType.choices, unique=True, verbose_name='Тип')
	url = models.URLField(max_length=500, blank=True, verbose_name='Ссылка', help_text='Например: https://t.me/your_channel')
	updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

	class Meta:
		verbose_name = 'Ссылка на соцсеть'
		verbose_name_plural = 'Ссылки на соцсети'
		ordering = ['social_type']

	def __str__(self):
		return f"{self.get_social_type_display()}"
