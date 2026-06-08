import logging
from datetime import timedelta
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import Tournament, TournamentRegistration

logger = logging.getLogger(__name__)


def recalculate_user_rating(user_id: int) -> None:
    """
    Пересчитывает rating и knockouts пользователя.
    Итог = initial (задаётся вручную) + сумма очков/нокаутов из всех турниров.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    base = User.objects.filter(pk=user_id).values('rating_initial', 'knockouts_initial').first()
    if not base:
        return

    totals = TournamentRegistration.objects.filter(user_id=user_id).aggregate(
        total_points=Sum('points'),
        total_knockouts=Sum('knockouts'),
    )
    User.objects.filter(pk=user_id).update(
        rating=base['rating_initial'] + (totals['total_points'] or 0),
        knockouts=base['knockouts_initial'] + (totals['total_knockouts'] or 0),
    )


@receiver(post_save, sender=TournamentRegistration)
def recalculate_on_registration_save(sender, instance: TournamentRegistration, **kwargs):
    recalculate_user_rating(instance.user_id)


@receiver(post_delete, sender=TournamentRegistration)
def recalculate_on_registration_delete(sender, instance: TournamentRegistration, **kwargs):
    recalculate_user_rating(instance.user_id)


@receiver(post_save, sender=Tournament)
def schedule_tournament_lifecycle(sender, instance: Tournament, created, **kwargs):
    from celery_app.tasks.tournament import tournament_lifecycle_task

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
