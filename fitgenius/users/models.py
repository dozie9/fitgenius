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

    def get_full_name_or_username(self) -> str:
        if self.get_full_name():
            return self.get_full_name()
        return self.username

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

    def get_current_month_sales(self):
        today = timezone.now().date()
        offer_qs = self.offer_set.agent_sales(agent_uuid=self.uuid).filter(
            date__year=today.year, date__month=today.month)

        # offer_dict = OfferSerializer(offer_qs, many=True)

        sales = offer_qs.aggregate(sales=Sum('total_sales'))
        return 0 if sales['sales'] is None else sales['sales']

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

    def get_referrals(self, client_type=None):
        if client_type:
            return self.offer_set.filter(client_type=client_type).aggregate(sum=Sum('referrals'))['sum']
        return self.offer_set.all().aggregate(sum=Sum('referrals'))['sum']

    def get_sales(self, client_type=None):
        offer_qs = self.offer_set.agent_sales(agent_uuid=self.uuid)
        if not client_type:

            sales = offer_qs.aggregate(sales=Sum('total_sales'))['sales']
            return 0 if sales is None else sales
        sales = offer_qs.filter(client_type=client_type).aggregate(sales=Sum('total_sales'))['sales']
        return 0 if sales is None else sales

    def get_percent_sales_on_global(self, client_type):
        # from fitgenius.club.models import Offer
        global_sales = self.get_sales()
        client_type_sales = 0 if self.get_sales(client_type) is None else self.get_sales(client_type)

        try:
            return (client_type_sales / global_sales) * 100
        except ZeroDivisionError:
            return 0

    def get_number_of_sales(self, product_name='all', client_type=None, category=None):
        from fitgenius.club.models import OfferedItem

        offered_items = OfferedItem.objects.agent_offered_items(self.uuid)
        if client_type:
            offered_items = offered_items.filter(offer__client_type=client_type)
        if category:
            offered_items = offered_items.filter(offer__category=category)

        if product_name == 'all':
            return offered_items.count()
        offered_items = offered_items.filter(product__title=product_name)
        return offered_items.count()

    def get_number_prospect_sales(self):
        from fitgenius.club.models import Offer
        return self.get_number_of_sales(client_type=Offer.NEW_CLIENT, category=Offer.PROSPECT)

    def get_number_comeback_sales(self):
        from fitgenius.club.models import Offer
        return self.get_number_of_sales(client_type=Offer.NEW_CLIENT, category=Offer.COMEBACK)

    def get_number_prospect_finalized_sales(self):
        from fitgenius.club.models import Offer, OfferedItem

        offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(
            offer__client_type=Offer.NEW_CLIENT, offer__category=Offer.PROSPECT, offer__accepted=True)
        return offered_items.count()

    def get_number_prospect_nonfinalized_sales(self):
        from fitgenius.club.models import Offer, OfferedItem

        offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(
            offer__client_type=Offer.NEW_CLIENT, offer__category=Offer.PROSPECT, offer__accepted=False)
        return offered_items.count()

    def get_percentage_prospect_finalized(self):
        try:
            return (self.get_number_prospect_finalized_sales() / self.get_number_prospect_sales()) * 100
        except ZeroDivisionError:
            return 0

    def get_number_comeback_finalized_sales(self):
        from fitgenius.club.models import Offer, OfferedItem

        offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(
            offer__client_type=Offer.NEW_CLIENT, offer__category=Offer.COMEBACK, offer__accepted=True)
        return offered_items.count()

    def get_percentage_total_finalized(self):
        """filtered by new client"""
        try:
            return (self.get_number_prospect_finalized_sales() + self.get_number_comeback_finalized_sales()) * 100 / (
                self.get_number_prospect_sales() + self.get_number_comeback_sales())
        except ZeroDivisionError:
            return 0

    def ref_sales_ratio(self, client_type=None):
        # TODO: Get clarification
        try:
            if client_type:
                return self.get_referrals(client_type=client_type)/self.get_sales(client_type=client_type)
            return self.get_referrals()/self.get_sales()
        except decimal.InvalidOperation:
            return 0

    def finalized_sales_on_ref(self):
        # from fitgenius.club.models import Offer
        # offer_qs = self.offer_set.agent_sales(agent_uuid=self.uuid).filter(client_type=Offer.REFERRAL)
        #
        # sales = offer_qs.aggregate(sales=Sum('total_sales'))
        from fitgenius.club.models import OfferedItem, Offer

        offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(offer__category=Offer.REFERRAL, offer__accepted=True)
        return offered_items.count()

    def get_number_of_category(self, client_type):
        from fitgenius.club.models import Offer
        offers = self.offer_set.all()

    def finalized_new_clients(self):
        from fitgenius.club.models import Offer

        offers = self.offer_set.all()
        prospects = offers.filter(category=Offer.PROSPECT).count()
        comebacks = offers.filter(category=Offer.COMEBACK).count()
        finalized_prospects = offers.filter(category=Offer.PROSPECT, accepted=True).count()
        finalized_comebacks = offers.filter(category=Offer.COMEBACK, accepted=True).count()

        return ((finalized_prospects + finalized_comebacks) * 100) / (prospects + comebacks)

    def get_sales_for_product(self, product_title, client_type=None):
        from fitgenius.club.utils import product_totals

        product_sales = product_totals(self.uuid, client_type=client_type)
        # print(product_sales)
        try:
            membership_sales = next(x['total'] for x in product_sales if x['product'] == product_title)
            return membership_sales
        except StopIteration:
            return 0

    def get_sub_gt_14months(self, client_type=None):
        from fitgenius.club.models import OfferedItem, Offer
        if client_type:
            return OfferedItem.objects.agent_offered_items(self.uuid).filter(
                number_of_months__gt=14, offer__client_type=client_type).count()
        return OfferedItem.objects.agent_offered_items(self.uuid).filter(number_of_months__gt=14).count()

    def get_number_of_sub_for_range(self, min_months, max_months, client_type=None):
        from fitgenius.club.models import OfferedItem, Offer

        if client_type:
            return OfferedItem.objects.agent_offered_items(self.uuid).filter(
                number_of_months__range=(min_months, max_months), offer__client_type=client_type
            ).count()

        return OfferedItem.objects.agent_offered_items(self.uuid).filter(
            number_of_months__range=(min_months, max_months)
        ).count()

    def get_all_total_sub_months(self, client_type=None):
        """Total Months"""
        from fitgenius.club.models import OfferedItem, Offer
        if client_type:
            total = OfferedItem.objects.agent_offered_items(self.uuid).filter(offer__client_type=client_type).aggregate(sum=Sum('number_of_months'))['sum']
        else:
            total = OfferedItem.objects.agent_offered_items(self.uuid).aggregate(sum=Sum('number_of_months'))['sum']
        if total is None:
            return 0
        return total

    def get_average_month(self, client_type=None):
        try:
            if client_type:
                return self.get_sales_for_product('Membership', client_type=client_type) / self.get_all_total_sub_months(client_type=client_type)
            return self.get_sales_for_product('Membership')/self.get_all_total_sub_months()
        except ZeroDivisionError:
            return 0

    def get_average_membership_sale(self, client_type=None):
        try:
            if client_type:
                return self.get_sales_for_product('Membership', client_type=client_type) / self.get_number_of_sales('Membership', client_type=client_type)
            return self.get_sales_for_product('Membership') / self.get_number_of_sales('Membership')
        except ZeroDivisionError:
            return 0

    def get_percentage_scheduled_work(self):
        return 0

