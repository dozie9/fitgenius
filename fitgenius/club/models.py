from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Club(models.Model):
    name = models.CharField(max_length=255)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clubs')
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=18, decimal_places=2)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True)


class Budget(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    working_days = models.PositiveIntegerField(help_text=_("Number of working days"), default=23)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.agent.username


class OfferedItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    number_of_months = models.PositiveIntegerField()

    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Offer(models.Model):
    NEW_CLIENT = 'new client'
    ACTIVE_CLIENT = 'active client'
    EX_CLIENT = 'ex-client'
    LEAD = 'lead'
    REFERRAL = 'referral'
    GUEST = 'guest'
    CROSS_UPGRADE = 'cross & upgrade'

    CLIENT_TYPES = (
        (NEW_CLIENT, NEW_CLIENT.title()),
        (ACTIVE_CLIENT, ACTIVE_CLIENT.title()),
        (EX_CLIENT, EX_CLIENT.title()),
        (LEAD, LEAD.title()),
        (REFERRAL, REFERRAL.title()),
        (GUEST, GUEST.title()),
        (CROSS_UPGRADE, CROSS_UPGRADE.title()),
    )

    SPONTANEOUS = 'spontaneous'
    COMEBACK = 'comeback'

    MEETING_CHOICE = (
        (SPONTANEOUS, SPONTANEOUS.title()),
        (COMEBACK, COMEBACK.title())
    )

    PROSPECT = 'prospect'

    CATEGORY_CHOICE = (
        (COMEBACK, COMEBACK.title()),
        (PROSPECT, PROSPECT.title())
    )

    client_type = models.CharField(max_length=255, choices=CLIENT_TYPES)
    offered_items = models.ManyToManyField(OfferedItem, related_name='offfers')
    meeting_type = models.CharField(max_length=255, choices=MEETING_CHOICE)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICE)
    accepted = models.BooleanField()
    referrals = models.PositiveIntegerField(default=0)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=timezone.now)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'#{self.id} {self.agent.username}'


class Action(models.Model):
    MISS_NEW = 'miss new'
    MISS_ACTIVE = 'miss active'
    MISS_EX_CLIENT = 'miss ex client'
    MISS_LEAD = 'miss lead'
    MISS_REFERRAL = 'miss referral'
    MISS_GUEST = 'miss guest'
    EX_CLIENT = 'ex client'
    ACTIVE_CLIENT = 'active client'
    LEAD = 'lead'
    REFERRAL = 'referral'
    GUEST = 'guest'
    INFO = 'info'
    RELATION = 'relation'
    OTHER = 'other'

    CATEGORY_CHOICES = (
        (MISS_NEW, MISS_NEW.title()),
        (MISS_ACTIVE, MISS_ACTIVE.title()),
        (MISS_EX_CLIENT, MISS_EX_CLIENT.title()),
        (MISS_LEAD, MISS_LEAD.title()),
        (MISS_REFERRAL, MISS_REFERRAL.title()),
        (MISS_GUEST, MISS_GUEST.title()),
        (EX_CLIENT, EX_CLIENT.title()),
        (ACTIVE_CLIENT, ACTIVE_CLIENT.title()),
        (LEAD, LEAD.title()),
        (REFERRAL, REFERRAL.title()),
        (GUEST, GUEST.title()),
        (INFO, INFO.title()),
        (RELATION, RELATION.title()),
        (OTHER, OTHER.title()),
    )

    MISSED_CALLS = 'missed calls'
    CALLS = 'calls'
    EMAIL = 'e-mails'
    MESSAGE = 'message'
    BOOKED_MEETINGS = 'booked meetings'
    NO_SHOW = 'no show'
    EXTRA_REFERRALS = 'extra referrals'

    ACTION_CHOICES = (
        (MISSED_CALLS, MISSED_CALLS.title()),
        (CALLS, CALLS.title()),
        (EMAIL, EMAIL.title()),
        (MESSAGE, MESSAGE.title()),
        (BOOKED_MEETINGS, BOOKED_MEETINGS.title()),
        (NO_SHOW, NO_SHOW.title()),
        (EXTRA_REFERRALS, EXTRA_REFERRALS.title()),
    )

    time_spent = models.PositiveIntegerField(help_text=_('time in seconds'), default=0)
    amount = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    action = models.CharField(max_length=255, choices=ACTION_CHOICES)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=timezone.now)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.date} {self.action}'

    def get_absolute_url(self):
        return reverse('action-detail', kwargs={'pk': self.pk})

