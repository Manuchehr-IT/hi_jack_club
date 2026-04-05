from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import format_html
from django_ckeditor_5.fields import CKEditor5Field

class AboutClub(models.Model):
	sort_order = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Порядок сортировки")

	text = CKEditor5Field(blank=True, null=True, verbose_name="Текст")

	is_active = models.BooleanField(default=True, verbose_name="Активен")

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

	class Meta:
		verbose_name = "Блок 'О клубе'"
		verbose_name_plural = "Блоки 'О клубе'"
		ordering = ["sort_order", "-created_at"]

	def __str__(self):
		return f"Блок #{self.id}"

	def clean(self):
		"""Проверка, что хотя бы одно поле заполнено"""
		super().clean()

		has_text = bool(self.text and self.text.strip())
		has_images = self.block_images.exists() if self.pk else False

		if not has_text and not has_images:
			raise ValidationError("Заполните хотя бы одно поле: 'Текст' или добавьте 'Изображения'")

	def get_block_type(self):
		"""Определяем тип блока динамически"""
		has_text = bool(self.text and self.text.strip())
		has_images = self.block_images.exists()

		if has_text and has_images:
			return "mixed"
		elif has_text:
			return "text"
		elif has_images:
			return "gallery"
		else:
			return "empty"

	def get_image_count(self):
		return self.block_images.count()
	get_image_count.short_description = "Кол-во изображений"

	def images_preview(self):
		"""Превью изображений для списка в админке"""
		images = self.block_images.all()[:5]  # Показываем до 5 изображений
		if not images:
			return "Нет изображений"
		
		html = '<div style="display: flex; gap: 5px; flex-wrap: wrap;">'
		for img in images:
			html += format_html(
				'<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 3px;" title="{}" />',
				img.image.url,
				img.alt or img.filename()
			)
		html += '</div>'
		
		if self.block_images.count() > 5:
			html += f'<div style="margin-top: 5px; color: #666; font-size: 12px;">+ ещё {self.block_images.count() - 5}</div>'
		
		return format_html(html)
	images_preview.short_description = "Изображения"

class AboutClubImage(models.Model):
	block = models.ForeignKey(AboutClub, on_delete=models.CASCADE, related_name="block_images", verbose_name="Блок")
	image = models.ImageField(upload_to="about/blocks/", verbose_name="Изображение")
	alt = models.CharField(max_length=255, blank=True, verbose_name="Alt текст", help_text="Описание изображения для SEO и доступности")
	sort_order = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Порядок сортировки")
	uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

	class Meta:
		verbose_name = "Изображение блока"
		verbose_name_plural = "Изображения блока"
		ordering = ['sort_order', '-uploaded_at']
		indexes = [models.Index(fields=['block', 'sort_order'])]

	def __str__(self):
		return self.alt or f"Изображение #{self.id}"

	def filename(self):
		return os.path.basename(self.image.name)

	def thumbnail_preview(self):
		if self.image:
			return format_html(
				'<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />',
				self.image.url
			)
		return "Нет изображения"
	thumbnail_preview.short_description = "Миниатюра"

	def image_preview(self):
		if self.image and hasattr(self.image, 'url'):
			return format_html(
				'<img src="{}" width="100" height="100" style="object-fit: cover; border-radius:4px;" />',
				self.image.url
			)
		# return format_html('<img src="" width="100" height="100" style="object-fit: cover; border-radius:4px; background:#f0f0f0;" />')
		return format_html('<span style="color: #999;">Нет изображения</span>')
	image_preview.short_description = "Превью"
