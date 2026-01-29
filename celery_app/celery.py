import logging
from celery import Celery

from .config import settings

logger = logging.getLogger(__name__)

app = Celery(
	"celery",
	broker=settings.celery.broker_url,
	backend=None,
)

app.autodiscover_tasks(["celery_app.tasks"])

logger.info("Celery application configured with Redis at %s", settings.celery.broker_url)
