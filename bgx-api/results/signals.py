"""
Signals for automatic recalculation of results
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import RaceDayResult
from .calculations import recalculate_all


@receiver(post_save, sender=RaceDayResult)
def recalculate_on_result_save(sender, instance, created, **kwargs):
    """
    Recalculate race and championship results when a race day result is saved
    """
    race = instance.race_day.race
    recalculate_all(race=race)


@receiver(post_delete, sender=RaceDayResult)
def recalculate_on_result_delete(sender, instance, **kwargs):
    """
    Recalculate race and championship results when a race day result is deleted
    """
    race = instance.race_day.race
    recalculate_all(race=race)

