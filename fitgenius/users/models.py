import uuid
import decimal

from django.contrib.auth.models import AbstractUser
from django.db.models import (CharField, ForeignKey, CASCADE, UUIDField, Sum, Count)
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for FitGenius.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    # name = CharField(_("Name of User"), blank=True, max_length=255)
    # first_name = None  # type: ignore
    last_name = CharField(_("Surname"), blank=True, max_length=255)

    MANAGER = 'manager'
    AGENT = 'agent'

    ROLES = (
        (MANAGER, MANAGER.title()),
        (AGENT, AGENT.title()),
    )

    user_type = CharField(_("Role"), choices=ROLES, default=AGENT, max_length=255, null=True)
    club = ForeignKey('club.Club', on_delete=CASCADE, null=True)
    uuid = UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def get_time_worked(self):
        # from fitgenius.club.models import WorkingHour
        time_worked = self.workinghour_set.filter(
            date__lte=timezone.now().date()
        ).aggregate(total_hours=Sum('hours'))['total_hours']

        if time_worked is None:
            return 0
        return time_worked

    def get_current_day_sales(self):
        today = timezone.now().date()
        offer_qs = self.offer_set.agent_sales(agent_uuid=self.uuid).filter(
            date__year=today.year, date__month=today.month, date__day=today.day)
        sales = offer_qs.aggregate(sales=Sum('total_sales'))

        if sales['sales'] is None:
            return 0

        return sales['sales']

    def get_efficiency(self):
        # from fitgenius.club.models import Action
        # actions = Action.objects.filter(agent=self)
        total_time_spent = self.action_set.all().aggregate(total=Sum('time_spent'))['total']
        time_worked = self.get_time_worked()

        if total_time_spent is None or time_worked == 0:
            return 0
        return (total_time_spent * 100) / time_worked

    def get_call_per_hour(self):
        from fitgenius.club.models import Action
        no_calls = self.action_set.filter(action=Action.CALLS).count()
        if no_calls == 0:
            return 0
        return self.get_time_worked()/no_calls

    def get_referrals(self):
        return self.offer_set.all().aggregate(sum=Sum('referrals'))['sum']

    def get_sales(self):
        offer_qs = self.offer_set.agent_sales(agent_uuid=self.uuid)

        sales = offer_qs.aggregate(sales=Sum('total_sales'))
        return sales['sales']

    def ref_sales_ratio(self):
        try:
            return self.get_referrals()/self.get_sales()
        except decimal.InvalidOperation:
            return 0

    def finalized_sales_on_ref(self):
        from fitgenius.club.models import Offer
        offer_qs = self.offer_set.agent_sales(agent_uuid=self.uuid).filter(client_type=Offer.REFERRAL)

        sales = offer_qs.aggregate(sales=Sum('total_sales'))
        return sales['sales']

    def finalized_new_clients(self):
        from fitgenius.club.models import Offer

        offers = self.offer_set.all()
        prospects = offers.filter(category=Offer.PROSPECT).count()
        comebacks = offers.filter(category=Offer.COMEBACK).count()
        finalized_prospects = offers.filter(category=Offer.PROSPECT, accepted=True).count()
        finalized_comebacks = offers.filter(category=Offer.COMEBACK, accepted=True).count()

        return ((finalized_prospects + finalized_comebacks) * 100) / (prospects + comebacks)
