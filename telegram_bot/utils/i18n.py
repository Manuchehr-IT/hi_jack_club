import yaml  # Необходимо установить: pip install pyyaml
import os
from pathlib import Path
from typing import Any, Dict

class Translator:
	def __init__(self, locale_dir: str = "locales", default_lang: str = "ru"):
		self.locale_dir = Path(__file__).parent.parent / locale_dir
		self.default_lang = default_lang
		self.translations = self._load_translations()

	def _load_translations(self) -> dict:
		translations = {}
		for lang in os.listdir(self.locale_dir):
			lang_dir = self.locale_dir / lang
			if lang_dir.is_dir():
				translations[lang] = {}

				for yaml_file in lang_dir.glob("**/*.yaml"):
					rel_path = yaml_file.relative_to(lang_dir)
					namespace = str(rel_path.with_suffix('')).replace(os.sep, '.')

					with open(yaml_file, "r", encoding="utf-8") as f:
						translations[lang][namespace] = yaml.safe_load(f)
		return translations

	def _format_dict(self, data: dict, **kwargs) -> dict:
		"""Рекурсивно форматирует все строки в словаре."""
		formatted = {}
		for key, value in data.items():
			if isinstance(value, dict):
				formatted[key] = self._format_dict(value, **kwargs)
			elif isinstance(value, str):
				try:
					formatted[key] = value.format(**kwargs) if kwargs else value
				except KeyError as e:
					formatted[key] = value  # Оставляем как есть, если нет ключа для замены
			else:
				formatted[key] = value
		return formatted

	def translate(self, namespace: str, key: str | None = None, lang: str | None = None, **kwargs) -> Dict[str, Any] | str | None:
		lang = lang or self.default_lang
		try:
			translations = self.translations[lang][namespace]
			if key:
				value = translations
				for part in key.split("."):
					value = value[part]
				return value.format(**kwargs) if kwargs and isinstance(value, str) else value
			else:
				return self._format_dict(translations, **kwargs) if kwargs else translations
		except (KeyError, AttributeError):
			try:
				translations = self.translations[self.default_lang][namespace]
				if key:
					value = translations
					for part in key.split("."):
						value = value[part]
					return value.format(**kwargs) if kwargs and isinstance(value, str) else value
				else:
					return self._format_dict(translations, **kwargs) if kwargs else translations
			except (KeyError, AttributeError):
				return {
					"error": "Incorrect key or namespace, or incorrect format and its filling",
					"key": key,
					"namespace": namespace,
				}

i18n = Translator()