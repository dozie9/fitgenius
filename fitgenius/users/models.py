import datetime
import uuid
import decimal

from django.contrib.auth.models import AbstractUser
from django.db.models import (CharField, ForeignKey, ImageField, CASCADE, SET_NULL, UUIDField, Sum, Count)
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def get_user_image_dir(instance, filename):

    return "profile_pictures/{0}/{1}".format(instance.username, filename)


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
    club = ForeignKey('club.Club', on_delete=SET_NULL, null=True)
    uuid = UUIDField(default=uuid.uuid4, editable=False, unique=True)

    img = ImageField(_("Avatar"), upload_to=get_user_image_dir, null=True, blank=True)

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

    def get_img_url(self):
        if self.img and hasattr(self.img, 'url'):
            return self.img.url
        return '/static/images/users/avatar-1.jpg'

    def get_time_worked(self, **kwargs):
        # from fitgenius.club.models import WorkingHour
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        workinghour_qs = self.workinghour_set
        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)
            workinghour_qs = workinghour_qs.filter(date__range=[start_date, end_date])
        time_worked = workinghour_qs.filter(
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

    def get_efficiency(self, **kwargs):
        # from fitgenius.club.models import Action
        # actions = Action.objects.filter(agent=self)
        action_qs = self.action_set.all()
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)
            action_qs = action_qs.filter(date__range=[start_date, end_date])
        total_time_spent = action_qs.aggregate(total=Sum('time_spent'))['total']
        time_worked = self.get_time_worked(start_date=start_date, end_date=end_date)

        if total_time_spent is None or time_worked == 0:
            return 0
        return (total_time_spent * 100) / time_worked

    def get_call_per_hour(self):
        from fitgenius.club.models import Action
        no_calls = self.action_set.filter(action=Action.CALLS).count()
        if no_calls == 0:
            return 0
        return self.get_time_worked() / no_calls

    def get_referrals(self, client_type=None, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        offer_qs = self.offer_set.all()
        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)
            offer_qs = offer_qs.filter(date__range=[start_date, end_date])

        if client_type:
            total_ref = offer_qs.filter(client_type=client_type).aggregate(sum=Sum('referrals'))['sum']
            return 0 if total_ref is None else total_ref
        total_ref = offer_qs.aggregate(sum=Sum('referrals'))['sum']
        return 0 if total_ref is None else total_ref

    def get_no_extra_referrals(self, **kwargs):
        from fitgenius.club.models import Action

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        action_qs = self.action_set.filter(action=Action.EXTRA_REFERRALS)
        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)
            action_qs = action_qs.filter(date__range=[start_date, end_date])

        return action_qs.count()

    def get_ref_sales_ratio(self):
        pass

    def get_sales(self, client_type=None, meeting_type=None, category_type=None, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        offer_qs = self.offer_set.agent_sales(agent_uuid=self.uuid)
        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)
            offer_qs = offer_qs.filter(date__range=[start_date, end_date])
        if client_type:

            offer_qs = offer_qs.filter(client_type=client_type)

        if meeting_type:
            offer_qs = offer_qs.filter(meeting_type=meeting_type)

        if category_type:
            offer_qs = offer_qs.filter(category_type=category_type)

        sales = offer_qs.aggregate(sales=Sum('total_sales'))['sales']
        return 0 if sales is None else sales

    def get_percent_sales_on_global(self, client_type, **kwargs):
        # from fitgenius.club.models import Offer
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        global_sales = self.get_sales(start_date=start_date, end_date=end_date)
        client_type_sales = 0 if self.get_sales(client_type, start_date=start_date, end_date=end_date) is None else self.get_sales(client_type, start_date=start_date, end_date=end_date)

        try:
            return (client_type_sales / global_sales) * 100
        except ZeroDivisionError:
            return 0

    def get_number_of_sales(self, product_name='all', client_type=None, category=None, **kwargs):
        from fitgenius.club.models import OfferedItem

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        offered_items = OfferedItem.objects.agent_offered_items(self.uuid)

        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)
            offered_items = offered_items.filter(offer__date__range=[start_date, end_date])

        if client_type:
            offered_items = offered_items.filter(offer__client_type=client_type)
        if category:
            offered_items = offered_items.filter(offer__category=category)

        if product_name == 'all':
            return offered_items.count()
        offered_items = offered_items.filter(product__title=product_name)
        return offered_items.count()

    def get_number_prospect_sales(self, **kwargs):
        from fitgenius.club.models import Offer
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)

        return self.get_number_of_sales(client_type=Offer.NEW_CLIENT, category=Offer.PROSPECT, start_date=start_date, end_date=end_date)

    def get_number_comeback_sales(self, **kwargs):
        from fitgenius.club.models import Offer

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)

        return self.get_number_of_sales(client_type=Offer.NEW_CLIENT, category=Offer.COMEBACK, start_date=start_date, end_date=end_date)

    def get_number_prospect_finalized_sales(self, **kwargs):
        from fitgenius.club.models import Offer, OfferedItem

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(
            offer__client_type=Offer.NEW_CLIENT, offer__category=Offer.PROSPECT, offer__accepted=True)

        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)

            offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(
                offer__client_type=Offer.NEW_CLIENT, offer__category=Offer.PROSPECT, offer__accepted=True,
                offer__date__range=[start_date, end_date]
            )

        return offered_items.count()

    def get_number_prospect_nonfinalized_sales(self, **kwargs):
        from fitgenius.club.models import Offer, OfferedItem

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(
            offer__client_type=Offer.NEW_CLIENT, offer__category=Offer.PROSPECT, offer__accepted=False)

        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)

            offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(
                offer__client_type=Offer.NEW_CLIENT, offer__category=Offer.PROSPECT, offer__accepted=False,
                offer__date__range=[start_date, end_date]
            )

        return offered_items.count()

    def get_percentage_prospect_finalized(self, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        try:
            return (self.get_number_prospect_finalized_sales(start_date=start_date, end_date=end_date) / self.get_number_prospect_sales(start_date=start_date, end_date=end_date)) * 100
        except ZeroDivisionError:
            return 0

    def get_number_comeback_finalized_sales(self, **kwargs):
        from fitgenius.club.models import Offer, OfferedItem

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(
            offer__client_type=Offer.NEW_CLIENT, offer__category=Offer.COMEBACK, offer__accepted=True)

        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)
            offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(
                offer__client_type=Offer.NEW_CLIENT, offer__category=Offer.COMEBACK, offer__accepted=True,
                offer__date__range=[start_date, end_date]
            )

        return offered_items.count()

    def get_percentage_total_finalized(self, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        """filtered by new client"""
        try:
            return (self.get_number_prospect_finalized_sales(start_date=start_date, end_date=end_date) + self.get_number_comeback_finalized_sales(start_date=start_date, end_date=end_date)) * 100 / (
                self.get_number_prospect_sales(start_date=start_date, end_date=end_date) + self.get_number_comeback_sales(start_date=start_date, end_date=end_date))
        except ZeroDivisionError:
            return 0

    def ref_sales_ratio(self, client_type=None, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        # TODO: Get clarification
        try:
            if client_type:
                return (
                    (self.get_number_of_sales(product_name='Membership', client_type=client_type, start_date=start_date, end_date=end_date) +
                     self.get_number_of_sales(product_name='Service', client_type=client_type, start_date=start_date, end_date=end_date) +
                     self.get_number_of_sales(product_name='Carnet', client_type=client_type, start_date=start_date, end_date=end_date)
                     ) / self.get_referrals(client_type=client_type, start_date=start_date, end_date=end_date)
                )
            return (
                (self.get_number_of_sales(product_name='Membership', start_date=start_date, end_date=end_date) +
                 self.get_number_of_sales(product_name='Service', start_date=start_date, end_date=end_date) +
                 self.get_number_of_sales(product_name='Carnet', start_date=start_date, end_date=end_date)
                 ) / self.get_referrals(start_date=start_date, end_date=end_date)
            )
        except (decimal.InvalidOperation, ZeroDivisionError):
            return 0

    def total_ref_sales_ratio(self, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        try:
            return (
                (self.get_number_of_sales(product_name='Membership', start_date=start_date, end_date=end_date) +
                 self.get_number_of_sales(product_name='Service', start_date=start_date, end_date=end_date) +
                 self.get_number_of_sales(product_name='Carnet', start_date=start_date, end_date=end_date)
                 ) / self.get_referrals(start_date=start_date, end_date=end_date) + self.get_no_extra_referrals(start_date=start_date, end_date=end_date)
            )
        except ZeroDivisionError:
            return 0

    def finalized_sales_on_ref(self):
        # from fitgenius.club.models import Offer
        # offer_qs = self.offer_set.agent_sales(agent_uuid=self.uuid).filter(client_type=Offer.REFERRAL)
        #
        # sales = offer_qs.aggregate(sales=Sum('total_sales'))
        from fitgenius.club.models import OfferedItem, Offer

        offered_items = OfferedItem.objects.agent_offered_items(self.uuid).filter(offer__category=Offer.REFERRAL,
                                                                                  offer__accepted=True)
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

    def get_sales_for_product(self, product_title, client_type=None, **kwargs):
        from fitgenius.club.utils import product_totals

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        product_sales = product_totals(self.uuid, client_type=client_type, start_date=start_date, end_date=end_date)
        # print(product_sales)
        try:
            membership_sales = next(x['total'] for x in product_sales if x['product'] == product_title)
            return membership_sales
        except StopIteration:
            return 0

    def get_sub_gt_14months(self, client_type=None, **kwargs):
        from fitgenius.club.models import OfferedItem, Offer
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        offered_item_qs = OfferedItem.objects.agent_offered_items(self.uuid).filter(number_of_months__gt=14)

        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)

            offered_item_qs = offered_item_qs.filter(offer__date__range=[start_date, end_date])

        if client_type:
            offered_item_qs = offered_item_qs.filter(
                number_of_months__gt=14, offer__client_type=client_type)
        return offered_item_qs.count()

    def get_number_of_sub_for_range(self, min_months, max_months, client_type=None, **kwargs):
        from fitgenius.club.models import OfferedItem, Offer

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        offered_item_qs = OfferedItem.objects.agent_offered_items(self.uuid).filter(
            number_of_months__range=(min_months, max_months)
        )
        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)
            offered_item_qs = offered_item_qs.filter(offer__date__range=[start_date, end_date])

        if client_type:
            offered_item_qs = offered_item_qs.filter(
                number_of_months__range=(min_months, max_months), offer__client_type=client_type
            )

        return offered_item_qs.count()

    def get_all_total_sub_months(self, client_type=None, **kwargs):
        """Total Months"""
        from fitgenius.club.models import OfferedItem, Offer
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        offered_item_qs = OfferedItem.objects.agent_offered_items(self.uuid)
        if start_date:
            if not end_date:
                end_date = start_date + datetime.timedelta(days=1)
            else:
                end_date = end_date + datetime.timedelta(days=1)
            offered_item_qs = offered_item_qs.filter(offer__date__range=[start_date, end_date])
        if client_type:
            total = offered_item_qs.filter(offer__client_type=client_type).aggregate(
                sum=Sum('number_of_months'))['sum']
        else:
            total = OfferedItem.objects.agent_offered_items(self.uuid).aggregate(sum=Sum('number_of_months'))['sum']
        if total is None:
            return 0
        return total

    def get_average_month(self, client_type=None, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        try:
            if client_type:
                return self.get_sales_for_product('Membership',
                                                  client_type=client_type, start_date=start_date, end_date=end_date) / self.get_all_total_sub_months(
                    client_type=client_type, start_date=start_date, end_date=end_date)
            return self.get_sales_for_product('Membership', start_date=start_date, end_date=end_date) / self.get_all_total_sub_months(start_date=start_date, end_date=end_date)
        except ZeroDivisionError:
            return 0

    def get_average_membership_sale(self, client_type=None, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        try:
            if client_type:
                return self.get_sales_for_product('Membership', client_type=client_type, start_date=start_date, end_date=end_date) / self.get_number_of_sales(
                    'Membership', client_type=client_type, start_date=start_date, end_date=end_date)
            return self.get_sales_for_product('Membership', start_date=start_date, end_date=end_date) / self.get_number_of_sales('Membership', start_date=start_date, end_date=end_date)
        except ZeroDivisionError:
            return 0

    def get_percentage_scheduled_work(self, client_type=None, **kwargs):
        from fitgenius.club.models import Offer

        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        try:
            if client_type:
                scheduled_sale = self.get_sales(client_type=client_type, meeting_type=Offer.BOOKED, start_date=start_date, end_date=end_date)
                return (scheduled_sale * 100) / self.get_sales(client_type=client_type, start_date=start_date, end_date=end_date)
            scheduled_sale = self.get_sales(meeting_type=Offer.BOOKED, start_date=start_date, end_date=end_date)
            return (scheduled_sale * 100) / self.get_sales(start_date=start_date, end_date=end_date)
        except ZeroDivisionError:
            return 0

    def get_month_budget(self, month):
        month_ = month.month
        year = month.year
        budget_qs = self.budget_set.filter(club=self.club, month__year=year, month__month=month_)
        if budget_qs.exists():
            budget = budget_qs.first()
            return budget
        else:
            return 0

    def get_days_budget(self, date):
        month_budget = self.get_month_budget(date)
        if month_budget:
            return month_budget.amount / month_budget.working_days
        return 0

    def get_budget_for_range(self, start_date, end_date=None):
        from fitgenius.club.models import Budget

        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)

        budget_qs = Budget.objects.filter(
            club=self.club, agent=self,
            month__gte=start_date,

            month__lte=end_date,
        )
        # print(budget_qs)
        total = budget_qs.aggregate(total=Sum('amount'))['total']
        if total is None:
            return 0
        return total

    def get_workingdays_for_range(self, start_date, end_date=None):
        from fitgenius.club.models import Budget

        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)

        budget_qs = Budget.objects.filter(
            club=self.club, agent=self,
            month__year__gte=start_date.year,
            month__year__lte=end_date.year,
            month__month__gte=start_date.month,
            month__month__lte=end_date.month
        )
        total = budget_qs.aggregate(total=Sum('working_days'))['total']
        if total is None:
            return 0
        return total

    def get_days_worked(self, start_date, end_date=None):
        # from fitgenius.club.models import Action
        # Action.objects.filter(date__range=[start_date, end_date]).values('date').annotate(date_count=Count('date'))
        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)
        user_actions = self.action_set.filter(date__range=[start_date, end_date]).values('date').annotate(
            date_count=Count('date'))

        return user_actions.count()

    def get_budget_progress(self, start_date, end_date=None):

        try:
            budget_progress = (self.get_budget_for_range(start_date, end_date) / self.get_workingdays_for_range(
                start_date,
                end_date)
                               ) * self.get_days_worked(start_date, end_date)
            # print('progr', budget_progress)
            return budget_progress
        except ZeroDivisionError:
            return 0

    def get_current_sales(self, start_date, end_date=None):
        offer_qs = self.offer_set.agent_sales(agent_uuid=self.uuid)
        # print(offer_qs)
        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)

        sales = offer_qs.filter(date__range=[start_date, end_date]).aggregate(sales=Sum('total_sales'))['sales']
        return 0 if sales is None else sales

    def get_trend(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date + datetime.timedelta(days=1)

        try:
            trend = ((decimal.Decimal(self.get_current_sales(start_date, end_date)) * 100) / decimal.Decimal(self.get_budget_progress(start_date,
                                                                                                     end_date))) - 100
            return trend
        except (ZeroDivisionError, decimal.InvalidOperation):
            return 0
