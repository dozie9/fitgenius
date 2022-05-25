import pandas as pd

from django.core.serializers import serialize
from django.db.models import OuterRef, F, Sum, Subquery, Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
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

    return 0 if sales['sales'] is None else sales['sales'], 0 if budget['amount'] is None else budget['amount']


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


def product_totals(agent_uuid, date=None, client_type=None):
    offered_items = OfferedItem.objects.agent_offered_items(agent_uuid)
    if date is not None:
        offered_items = offered_items.filter(offer__date__year=date.year, offer__date__month=date.month)
    if client_type:
        offered_items = offered_items.filter(offer__client_type=client_type)
    products = Product.objects.all()

    totals = []
    for product in products:
        total = offered_items.filter(product=product).aggregate(total=Sum('price'))['total']
        totals.append({
            'product': product.title,
            'total': 0 if total is None else total
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


def generate_report(agents, report_type=None):
    if report_type == 'new_client':
        dataset = [
            {'Global Salse': agent.get_sales(client_type=Offer.NEW_CLIENT),
             'Memberships': agent.get_sales_for_product('Membership', client_type=Offer.NEW_CLIENT),
             'Services': agent.get_sales_for_product('Services', client_type=Offer.NEW_CLIENT),
             'Carnets': agent.get_sales_for_product('Carnets', client_type=Offer.NEW_CLIENT),
             'Fees': agent.get_sales_for_product('Fees', client_type=Offer.NEW_CLIENT),
             '%Sales on Global': agent.get_percent_sales_on_global(client_type=Offer.NEW_CLIENT),
             'Prospects': agent.get_number_of_sales(client_type=Offer.NEW_CLIENT, category=Offer.PROSPECT),
             'Prospects Finalized': agent.get_number_prospect_finalized_sales(),
             'Prospects Non Finalized': agent.get_number_prospect_nonfinalized_sales(),
             '% Prospects Finalized': agent.get_percentage_prospect_finalized(),
             'Comebacks': agent.get_number_of_sales(client_type=Offer.NEW_CLIENT, category=Offer.COMEBACK),
             '% Total Finalized': agent.get_percentage_total_finalized(),
             '#Total Sales': agent.get_number_of_sales(product_name='all', client_type=Offer.NEW_CLIENT),

             'No. Carnet Sales': agent.get_number_of_sales('Carnet', client_type=Offer.NEW_CLIENT),
             'No. Membership Sales': agent.get_number_of_sales('Membership', client_type=Offer.NEW_CLIENT),
             'No. Fees': agent.get_number_of_sales('Fee', client_type=Offer.NEW_CLIENT),
             'No. Services': agent.get_number_of_sales('Service', client_type=Offer.NEW_CLIENT),
             'Referrals': agent.get_referrals(client_type=Offer.NEW_CLIENT),
             'Extra Referrals': 0,  # TODO: Get clarification
             'Ref/Sale': 0,  # TODO: Get clarification
             'Total Ref/Sale': 0,  # TODO: Get clarification
             '>14 months': agent.get_sub_gt_14months(client_type=Offer.NEW_CLIENT),
             'Yearly 12-14 months': agent.get_number_of_sub_for_range(12, 14, client_type=Offer.NEW_CLIENT),
             'Seasonal 6-11 months': agent.get_number_of_sub_for_range(6, 11, client_type=Offer.NEW_CLIENT),
             'Trim. 3-5 months': agent.get_number_of_sub_for_range(3, 5, client_type=Offer.NEW_CLIENT),
             'Monthly 1-2 months': agent.get_number_of_sub_for_range(1, 2, client_type=Offer.NEW_CLIENT),
             'Other': 0,  # TODO: Get clarification
             'Total Months': agent.get_all_total_sub_months(client_type=Offer.NEW_CLIENT),
             'Average Month': agent.get_average_month(client_type=Offer.NEW_CLIENT),
             'Average Membership Sale': agent.get_average_membership_sale(client_type=Offer.NEW_CLIENT),
             'Outcome % Scheduled work': 0,  # TODO: Get clarification
             'agent': agent.username
             } for agent in agents]
    else:
        """global"""
        dataset = [
            {'Global Salse': agent.get_sales(),
             'Memberships': agent.get_sales_for_product('Membership'),
             'Services': agent.get_sales_for_product('Services'),
             'Carnets': agent.get_sales_for_product('Carnets'),
             'Fees': agent.get_sales_for_product('Fees'),
             'Time worked': agent.get_time_worked(),
             'Efficiency': agent.get_efficiency(),
             '#Total Sales': agent.get_number_of_sales(product_name='all'),
             'No. Carnet Sales': agent.get_number_of_sales('Carnet'),
             'No. Membership Sales': agent.get_number_of_sales('Membership'),
             'No. Fees': agent.get_number_of_sales('Fee'),
             'No. Services': agent.get_number_of_sales('Service'),
             'Referrals': agent.get_referrals(),
             'Extra Referrals': 0, # TODO: Get clarification
             'Ref/Sale': 0, # TODO: Get clarification
             'Total Ref/Sale': 0, # TODO: Get clarification
             '>14 months': agent.get_sub_gt_14months(),
             'Yearly 12-14 months': agent.get_number_of_sub_for_range(12, 14),
             'Seasonal 6-11 months': agent.get_number_of_sub_for_range(6, 11),
             'Trim. 3-5 months': agent.get_number_of_sub_for_range(3, 5),
             'Monthly 1-2 months': agent.get_number_of_sub_for_range(1, 2),
             'Other': 0, # TODO: Get clarification
             'Total Months': agent.get_all_total_sub_months(),
             'Average Month': agent.get_average_month(),
             'Average Membership Sale': agent.get_average_membership_sale(),
             'Outcome % Scheduled work': 0, # TODO: Get clarification
             'agent': agent.username
             } for agent in agents]
    # print(dataset)
    df = pd.DataFrame(dataset).set_index('agent')
    return df.append(df.sum().rename('Total'))


def export_file(data_frame, file_type):
    if file_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'
        data_frame.to_csv(response)
        return response
    if file_type == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
        data_frame.to_excel(response, engine="xlsxwriter")
        return response

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
