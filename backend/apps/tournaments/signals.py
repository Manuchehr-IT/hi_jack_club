# tournament/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Tournament
from celery_app.tasks.tournament import start_tournament_task

@receiver(post_save, sender=Tournament)
def schedule_tournament_start(sender, instance: Tournament, created, **kwargs):
	# турнир уже не в очереди — ничего не делаем
	if instance.status != Tournament.StatusType.IN_QUEUE:
		return

	# если дата старта в прошлом или сейчас — стартуем сразу
	if instance.started_at <= timezone.now():
		start_tournament_task.delay(instance.id)
		return

	# иначе планируем
	start_tournament_task.apply_async(
		args=[instance.id],
		eta=instance.started_at
	)
