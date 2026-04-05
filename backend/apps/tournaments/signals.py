import logging
from datetime import timedelta
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .factory import create_tournament_service
from .models import Tournament, TournamentEventLog
from celery_app.tasks.tournament import tournament_lifecycle_task

logger = logging.getLogger(__name__)

@receiver([post_save, post_delete], sender=TournamentEventLog)
def on_event_change(sender, instance, **kwargs):
	"""При изменении событий"""
	logger.info(f"TournamentEventLog on_event_change: {instance}, TournamentEventLog.user: {instance.user}")
	transaction.on_commit(lambda: instance.user.tournament_registrations.filter(tournament=instance.tournament).first().recalc_stats())


@receiver(post_save, sender=Tournament)
def schedule_tournament_lifecycle(sender, instance: Tournament, created, **kwargs):
	# expires_at = instance.started_at + timedelta(hours=9)
	expires_at = instance.started_at + timedelta(minutes=2)
	logger.info(f"SCHEDULE_TOURNAMENT_LIFECYCLE [expires_at]: {expires_at}")

	if instance.status == Tournament.StatusType.IN_QUEUE:
		if instance.started_at <= timezone.now():
			tournament_lifecycle_task.delay("start", instance.id)
		else:
			tournament_lifecycle_task.apply_async(args=["start", instance.id], eta=instance.started_at)

	elif instance.status == Tournament.StatusType.ACTIVE:
		if expires_at <= timezone.now():
			tournament_lifecycle_task.delay("finish", instance.id)
		else:
			tournament_lifecycle_task.apply_async(args=["finish", instance.id], eta=expires_at)

	elif instance.status == Tournament.StatusType.INACTIVE:
		if not instance.olap_report_completed:
			tournament_service = create_tournament_service()
			tournament_service.process_olap_report(instance.id)
