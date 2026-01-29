import importlib
from pathlib import Path
from aiogram import Router

def load_routers_recursive(base_dir: Path, package_prefix: str = "") -> Router:
	"""Рекурсивно загружает все роутеры из подпапок"""
	main_router = Router()

	for path in base_dir.glob("*"):
		if path.is_file() and path.suffix == ".py" and path.stem != "__init__":
			try:
				module = importlib.import_module(f"{package_prefix}{path.stem}")
				if hasattr(module, "router"):
					main_router.include_router(module.router)
					print(f"✓ Router loaded: {package_prefix}{path.stem}")
			except ImportError as e:
				print(f"⚠️ Failed to load {path}: {e}")

		elif path.is_dir():
			sub_router = load_routers_recursive(
				path,
				package_prefix=f"{package_prefix}{path.name}."
			)
			# if sub_router.handlers:  # Добавляем только если есть обработчики
			main_router.include_router(sub_router)

	return main_router

# Создаем корневой роутер
router = load_routers_recursive(Path(__file__).parent, "handlers.")
