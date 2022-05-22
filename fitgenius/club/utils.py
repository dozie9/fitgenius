from django.core.serializers import serialize
from django.db.models import OuterRef, F, Sum, Subquery, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.renderers import JSONRenderer

from fitgenius.club.models import OfferedItem, Offer, Budget, Product, Action, WorkingHour
from fitgenius.club.serializers import OfferSerializer, BudgetSerializer
from fitgenius.utils.query_debugger import query_debugger


# @query_debugger
def month_sale_vs_budget(agent_uuid, year, month):

    offer_qs = Offer.objects.agent_sales(agent_uuid=agent_uuid).filter(
        date__year=year, date__month=month)

    # offer_dict = OfferSerializer(offer_qs, many=True)

    sales = offer_qs.aggregate(sales=Sum('total_sales'))

    budget_qs = Budget.objects.filter(agent__uuid=agent_uuid, month__year=year, month__month=month)
    budget = budget_qs.aggregate(amount=Sum('amount'))
    # budget_dict = BudgetSerializer(budget_qs, many=True)

    return sales['sales'], budget['amount']


def current_day_sales(agent_uuid):
    today = timezone.now().date()
    offer_qs = Offer.objects.agent_sales(agent_uuid=agent_uuid).filter(
        date__year=today.year, date__month=today.month, date__day=today.day)
    sales = offer_qs.aggregate(sales=Sum('total_sales'))

    return sales['sales']


def efficiency(agent):
    actions = Action.objects.filter(agent__uuid=agent)
    total_time_spent = actions.aggregate(total=Sum('time_spent'))['total']

    if total_time_spent is None:
        return 0
    return (total_time_spent * 100) / agent.time_worked


def product_totals(agent_uuid, date=None):
    offered_items = OfferedItem.objects.agent_offered_items(agent_uuid)
    if date is not None:
        offered_items = offered_items.filter(offer__date__year=date.year, offer__date__month=date.month)
    products = Product.objects.all()

    totals = []
    for product in products:
        total = offered_items.filter(product=product).aggregate(total=Sum('price'))['total']
        totals.append({
            'product': product.title,
            'total': total
        })
    return totals


# @query_debugger
def product_sale_by_month(agent_uuid):
    offered_items = OfferedItem.objects.agent_offered_items(agent_uuid)
    sales_by_month = []
    for product in Product.objects.all():
        sales = offered_items.filter(product=product).annotate(
            month=TruncMonth('offer__date'), product_name=F('product__title')
        ).values('month', 'product_name').annotate(
            c=Count('id'), total_price=Sum('price')
        ).order_by('month')
        sales_by_month.append({'product': product.title, 'sales': list(sales)})
    return sales_by_month


# def agent_sales(agent_uuid):
#     offered_items_qs = OfferedItem.objects.filter(offer=OuterRef('pk')).annotate(
#         total_price=F('product__value') * F('quantity')
#     ).values('offer')
#
#     oi_sum = offered_items_qs.annotate(oi_sum=Sum('total_price')).values('oi_sum')
#
#     offer_qs = Offer.objects.filter(agent__uuid=agent_uuid).annotate(
#         total_sales=Subquery(oi_sum), no_product=Count('offereditem')
#     )
#     return offer_qs
