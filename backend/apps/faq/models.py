from django.db import models

class FAQ(models.Model):
	question = models.CharField(max_length=64, unique=True, null=False, blank=False, verbose_name="Вопрос")
	answer = models.TextField(null=False, blank=False, verbose_name="Ответ")
	sort_order = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Порядок сортировки")

	is_active = models.BooleanField(default=True)

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

	class Meta:
		verbose_name = "Вопрос-ответ"
		verbose_name_plural = "Вопросы-ответы"
		ordering = ["sort_order", "created_at"]

	def __str__(self):
		return self.question
