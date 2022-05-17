from django.core.serializers import serialize
from django.db.models import OuterRef, F, Sum, Subquery, Count
from rest_framework.renderers import JSONRenderer

from fitgenius.club.models import OfferedItem, Offer, Budget
from fitgenius.club.serializers import OfferSerializer, BudgetSerializer
from fitgenius.utils.query_debugger import query_debugger


@query_debugger
def total_month_sale(agent_uuid, year, month):
    offered_items_qs = OfferedItem.objects.filter(offer=OuterRef('pk')).annotate(
        total_price=F('product__value') * F('quantity')
    ).values('offer')

    oi_sum = offered_items_qs.annotate(oi_sum=Sum('total_price')).values('oi_sum')

    offer_qs = Offer.objects.filter(agent__uuid=agent_uuid, date__year=year, date__month=month).annotate(
        total_sales=Subquery(oi_sum)
    )

    # offer_dict = OfferSerializer(offer_qs, many=True)

    sales = offer_qs.aggregate(sales=Sum('total_sales'))

    budget_qs = Budget.objects.filter(agent__uuid=agent_uuid, month__year=year, month__month=month)
    budget = budget_qs.aggregate(amount=Sum('amount'))
    # budget_dict = BudgetSerializer(budget_qs, many=True)

    return sales, budget


def agent_sales(agent_uuid):
    offered_items_qs = OfferedItem.objects.filter(offer=OuterRef('pk')).annotate(
        total_price=F('product__value') * F('quantity')
    ).values('offer')

    oi_sum = offered_items_qs.annotate(oi_sum=Sum('total_price')).values('oi_sum')

    offer_qs = Offer.objects.filter(agent__uuid=agent_uuid).annotate(
        total_sales=Subquery(oi_sum), no_product=Count('offereditem')
    )
    return offer_qs
