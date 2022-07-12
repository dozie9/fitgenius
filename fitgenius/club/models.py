import uuid
import datetime
import decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import OuterRef, F, Sum, Subquery, Count
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify

User = get_user_model()


class Club(models.Model):
    name = models.CharField(max_length=255)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='clubs')
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name

    def get_time_worked(self):
        # from fitgenius.club.models import WorkingHour
        users = self.user_set.all()
        time_worked = sum([user.get_time_worked() for user in users])

        if time_worked is None:
            return 0
        return time_worked

    def get_current_day_sales(self):
        users = self.user_set.all()
        sales = sum([user.get_current_day_sales() for user in users])

        return sales

    def get_current_month_sales(self):
        users = self.user_set.all()
        sales = sum([user.get_current_month_sales() for user in users])

        return sales

    def get_referrals(self, client_type=None):
        users = self.user_set.all()
        try:
            referrals = sum([user.get_referrals() for user in users])
            return referrals
        except TypeError:
            return 0

    def get_sales(self, client_type=None):
        users = self.user_set.all()

        if not client_type:
            return sum([user.get_sales() for user in users])

        return sum([user.get_sales(client_type=client_type) for user in users])

    def finalized_sales_on_ref(self):
        # from fitgenius.club.models import Offer
        offer_qs = self.offer_set.agent_sales(agent_uuid=self.uuid).filter(client_type=Offer.REFERRAL)

        sales = offer_qs.aggregate(sales=Sum('total_sales'))
        return sales['sales']

    def ref_sales_ratio(self, client_type=None):
        # TODO: Get clarification
        try:
            if client_type:
                return self.get_referrals(client_type=client_type)/self.get_sales(client_type=client_type)
            return self.get_referrals()/self.get_sales()
        except decimal.InvalidOperation:
            return 0

    def get_call_per_hour(self):
        # from fitgenius.club.models import Action
        no_calls = self.action_set.filter(action=Action.CALLS).count()
        if no_calls == 0:
            return 0
        return self.get_time_worked()/no_calls

    def get_number_of_sales(self, product_name='all', client_type=None, category=None):
        users = self.user_set.all()

        return sum([user.get_number_of_sales(product_name=product_name, client_type=client_type, category=category) for user in users])

    def get_number_prospect_sales(self):
        # from fitgenius.club.models import Offer
        return self.get_number_of_sales(client_type=Offer.NEW_CLIENT, category=Offer.PROSPECT)

    def get_number_comeback_sales(self):
        # from fitgenius.club.models import Offer
        return self.get_number_of_sales(client_type=Offer.NEW_CLIENT, category=Offer.COMEBACK)

    def get_number_prospect_finalized_sales(self):
        users = self.user_set.all()
        return sum([user.get_number_prospect_finalized_sales() for user in users])

    def get_number_prospect_nonfinalized_sales(self):
        users = self.user_set.all()
        return sum([user.get_number_prospect_nonfinalized_sales() for user in users])

    def get_percentage_prospect_finalized(self):
        try:
            return (self.get_number_prospect_finalized_sales() / self.get_number_prospect_sales()) * 100
        except ZeroDivisionError:
            return 0

    def get_number_comeback_finalized_sales(self):
        users = self.user_set.all()
        return sum([user.get_number_comeback_finalized_sales() for user in users])

    def get_percentage_total_finalized(self):
        """filtered by new client"""
        try:
            return (self.get_number_prospect_finalized_sales() + self.get_number_comeback_finalized_sales()) * 100 / (
                self.get_number_prospect_sales() + self.get_number_comeback_sales())
        except ZeroDivisionError:
            return 0

    def get_days_budget(self, date):
        return sum([agent.get_days_budget(date) for agent in self.user_set.all()])

    def get_budget_for_range(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)
        users = self.user_set.all()
        return sum([agent.get_budget_for_range(start_date, end_date) for agent in users])

    def get_workingdays_for_range(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)
        users = self.user_set.all()
        return sum([agent.get_workingdays_for_range(start_date, end_date) for agent in users])

    def get_days_worked(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)
        users = self.user_set.all()
        return sum([agent.get_days_worked(start_date, end_date) for agent in users])

    def get_budget_progress(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)
        users = self.user_set.all()
        return sum([agent.get_budget_progress(start_date, end_date) for agent in users])

    def get_current_sales(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)
        users = self.user_set.all()
        return sum([agent.get_current_sales(start_date, end_date) for agent in users])

    def get_trend(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)

        try:
            trend = ((decimal.Decimal(self.get_current_sales(start_date, end_date)) * 100) / decimal.Decimal(self.get_budget_progress(start_date,
                                                                                                 end_date))) - 100
            return trend
        except (ZeroDivisionError, decimal.InvalidOperation):
            return 0


class Product(models.Model):
    title = models.CharField(max_length=255)
    # value = models.DecimalField(max_digits=18, decimal_places=2)
    # club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(null=False, unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class Budget(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    working_days = models.PositiveIntegerField(help_text=_("Number of working days"), default=23)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ['-month']
        unique_together = [
            ['agent', 'month']
        ]

    def __str__(self):
        return f'{self.agent.username} | {self.month} | {self.amount}'

    @property
    def get_daily_budget(self):
        return self.amount / self.working_days


class OfferedItemManager(models.Manager):
    def agent_offered_items(self, agent_uuid):
        return self.filter(offer__agent__uuid=agent_uuid)


class OfferedItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE, null=True)
    # quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    number_of_months = models.PositiveIntegerField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    objects = OfferedItemManager()

    def __str__(self):
        if self.number_of_months is not None:
            return f'{self.product} | {self.price} | {self.number_of_months} months'
        return f'{self.product} | {self.price}'


class OfferManager(models.Manager):

    def agent_sales(self, agent_uuid):
        offered_items_qs = OfferedItem.objects.filter(offer=OuterRef('pk')).annotate(
            total_price=F('price')
        ).values('offer')

        oi_sum = offered_items_qs.annotate(oi_sum=Sum('total_price')).values('oi_sum')

        offer_qs = self.filter(agent__uuid=agent_uuid).annotate(
            total_sales=Subquery(oi_sum), no_product=Count('offereditem')
        )
        return offer_qs


class Offer(models.Model):
    NEW_CLIENT = 'new client'
    ACTIVE_CLIENT = 'active client'
    EX_CLIENT = 'ex-client'
    LEAD = 'lead'
    REFERRAL = 'referral'
    GUEST = 'guest'
    CROSS_UPGRADE = 'cross upgrade'

    CLIENT_TYPES = (
        (NEW_CLIENT, NEW_CLIENT.title()),
        (ACTIVE_CLIENT, ACTIVE_CLIENT.title()),
        (EX_CLIENT, EX_CLIENT.title()),
        (LEAD, LEAD.title()),
        (REFERRAL, REFERRAL.title()),
        (GUEST, GUEST.title()),
        (CROSS_UPGRADE, 'cross & upgrade'.title()),
    )

    SPONTANEOUS = 'spontaneous'
    COMEBACK = 'comeback'
    BOOKED = 'booked'

    MEETING_CHOICE = (
        (SPONTANEOUS, SPONTANEOUS.title()),
        (BOOKED, BOOKED.title())
    )

    PROSPECT = 'prospect'

    CATEGORY_CHOICE = (
        (COMEBACK, COMEBACK.title()),
        (PROSPECT, PROSPECT.title())
    )

    client_type = models.CharField(max_length=255, choices=CLIENT_TYPES)
    # offered_items = models.ManyToManyField(OfferedItem, related_name='offfers')
    meeting_type = models.CharField(max_length=255, choices=MEETING_CHOICE)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICE)
    accepted = models.BooleanField()
    referrals = models.PositiveIntegerField(default=0)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True)
    date = models.DateField(default=datetime.date.today)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    objects = OfferManager()

    class Meta:
        ordering = ['-date']
        permissions = (
            ('access_offer', 'Access offer'),
        )

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
    date = models.DateField(default=datetime.date.today)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ['-date']
        permissions = (
            ('access_action', 'Access action'),
        )

    def __str__(self):
        return f'{self.date} {self.action}'

    @property
    def time_spent_mins(self):
        return self.time_spent / 60

    def get_absolute_url(self):
        return reverse('club:update-action', kwargs={'pk': self.pk})


class WorkingHour(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    hours = models.PositiveIntegerField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ['-date']
        unique_together = [
            ['agent', 'date']
        ]
        permissions = (
            ('access_working_hour', 'Access working hour'),
        )

    def __str__(self):
        return f"{self.agent.username} | {self.date.strftime('%m/%d/%Y')} | {self.hours}"
