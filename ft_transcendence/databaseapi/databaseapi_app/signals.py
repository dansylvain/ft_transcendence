from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Player, PlayerStatistics

# Signal handler that is triggered after a Player instance is saved
@receiver(post_save, sender=Player)
def create_player_statistics(sender, instance, created, **kwargs):
    if created:
        PlayerStatistics.objects.create(player=instance)
