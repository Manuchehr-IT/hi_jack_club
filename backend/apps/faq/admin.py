# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
	# Какие поля показывать в списке
	list_display = (
		'question_short',
		'answer_short', 
		'sort_order',
		'is_active',  # ← Прямо поле модели, будет чекбоксом
		'created_at',
		'updated_at',
	)

	# Поля для редактирования прямо в списке
	list_editable = ('sort_order', 'is_active')  # ← Добавили is_active сюда!

	# Фильтры справа
	list_filter = ('is_active', 'created_at')

	# Поиск по полям
	search_fields = ('question', 'answer')

	# Количество записей на странице
	list_per_page = 10

	# Поля в форме редактирования
	fieldsets = (
		('Основная информация', {
			'fields': ('question', 'answer', 'sort_order')
		}),
		('Статус', {
			'fields': ('is_active',),
		}),
		('Даты', {
			'fields': ('created_at', 'updated_at'),
		}),
	)

	# Только для чтения
	readonly_fields = ('created_at', 'updated_at')

	# Кастомные методы для отображения
	def question_short(self, obj):
		"""Сокращенный вопрос"""
		return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
	question_short.short_description = 'Вопрос'
	question_short.admin_order_field = 'question'  # ← Добавил для сортировки

	def answer_short(self, obj):
		"""Сокращенный ответ (без HTML тегов)"""
		import re
		text = re.sub(r'<[^>]+>', '', obj.answer)
		return text[:100] + '...' if len(text) > 100 else text
	answer_short.short_description = 'Ответ'
	answer_short.admin_order_field = 'answer'  # ← Добавил для сортировки

	# Автозаполнение (опционально)
	def get_readonly_fields(self, request, obj=None):
		"""Делаем created_at только для чтения"""
		if obj:  # Если объект уже существует
			return self.readonly_fields + ('created_at', 'updated_at')
		return self.readonly_fields
	
	# Действия в админке
	actions = ['make_active', 'make_inactive']

	def make_active(self, request, queryset):
		"""Активировать выбранные FAQ"""
		updated = queryset.update(is_active=True)
		self.message_user(request, f"{updated} FAQ активированы.")
	make_active.short_description = "Активировать выбранные FAQ"

	def make_inactive(self, request, queryset):
		"""Деактивировать выбранные FAQ"""
		updated = queryset.update(is_active=False)
		self.message_user(request, f"{updated} FAQ деактивированы.")
	make_inactive.short_description = "Деактивировать выбранные FAQ"
