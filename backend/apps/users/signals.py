from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


def _get_user_model():
    from django.contrib.auth import get_user_model
    return get_user_model()


@receiver(pre_save)
def track_user_initial_fields(sender, instance, **kwargs):
    """Запоминает, изменились ли начальные поля рейтинга до сохранения."""
    User = _get_user_model()
    if sender is not User:
        return

    if not instance.pk:
        instance._initial_rating_changed = False
        return

    try:
        old = User.objects.get(pk=instance.pk)
        instance._initial_rating_changed = (
            old.rating_initial != instance.rating_initial
            or old.knockouts_initial != instance.knockouts_initial
        )
    except User.DoesNotExist:
        instance._initial_rating_changed = False


@receiver(post_save)
def recalculate_on_initial_change(sender, instance, **kwargs):
    """При изменении rating_initial / knockouts_initial пересчитывает итоговый рейтинг."""
    User = _get_user_model()
    if sender is not User:
        return

    if getattr(instance, '_initial_rating_changed', False):
        from apps.tournaments.signals import recalculate_user_rating
        recalculate_user_rating(instance.pk)
