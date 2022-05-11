from django.db.models.signals import pre_save, post_save
from django.dispatch.dispatcher import receiver
from guardian.shortcuts import assign_perm

from .models import Action, Offer

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


@receiver(post_save, sender=Action)
def action_post_save(sender, instance: Action, created, **kwargs):
    if created:
        # assigning permission to agent
        assign_perm('access_action', instance.agent, instance)

        # assigning permission to manager
        assign_perm('access_action', instance.club.manager, instance)


@receiver(post_save, sender=Offer)
def offer_post_save(sender, instance: Offer, created, **kwargs):
    if created:
        # assigning offer to agent's club
        offer_qs = Offer.objects.filter(id=instance.id)
        offer_qs.update(club=instance.agent.club)

        # assigning permission to agent
        assign_perm('access_offer', instance.agent, instance)

        # assigning permission to manager
        assign_perm('access_offer', offer_qs.first().club.manager, instance)

