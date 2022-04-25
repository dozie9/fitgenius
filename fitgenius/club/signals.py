from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver

from .models import Action


action_time_dict = {
    Action.MISSED_CALLS: 30,
    Action.EMAIL: 120,
    Action.CALLS: 180,
    Action.MESSAGE: 60,
    Action.EXTRA_REFERRALS: 120,
    Action.BOOKED_MEETINGS: 0,
    Action.NO_SHOW: 0,
}


@receiver(pre_save, sender=Action)
def assign_action_time(sender, instance: Action, **kwargs):
    instance.time_spent = action_time_dict[instance.action]
