import calendar
import datetime
import itertools
from typing import Union, List

import pandas as pd
import numpy as np

from django.core.serializers import serialize
from django.db.models import OuterRef, F, Sum, Subquery, Count, QuerySet, Avg
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.renderers import JSONRenderer

from fitgenius.club.models import OfferedItem, Offer, Budget, Product, Action, WorkingHour, Club
from fitgenius.club.serializers import OfferSerializer, BudgetSerializer
from fitgenius.utils.query_debugger import query_debugger


# @query_debugger
from fitgenius.utils.utils import years_ago


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
    if not report_type == 'global':
        dataset = [
            {'Global Salse': agent.get_sales(client_type=report_type),
             'Memberships': agent.get_sales_for_product('Membership', client_type=report_type),
             'Services': agent.get_sales_for_product('Services', client_type=report_type),
             'Carnets': agent.get_sales_for_product('Carnets', client_type=report_type),
             'Fees': agent.get_sales_for_product('Fees', client_type=report_type),
             '%Sales on Global': agent.get_percent_sales_on_global(client_type=report_type),
             'Prospects': agent.get_number_of_sales(client_type=report_type, category=Offer.PROSPECT),
             'Prospects Finalized': agent.get_number_prospect_finalized_sales(),
             'Prospects Non Finalized': agent.get_number_prospect_nonfinalized_sales(),
             '% Prospects Finalized': agent.get_percentage_prospect_finalized(),
             'Comebacks': agent.get_number_of_sales(client_type=report_type, category=Offer.COMEBACK),
             '% Total Finalized': agent.get_percentage_total_finalized(),
             '#Total Sales': agent.get_number_of_sales(product_name='all', client_type=report_type),

             'No. Carnet Sales': agent.get_number_of_sales('Carnet', client_type=report_type),
             'No. Membership Sales': agent.get_number_of_sales('Membership', client_type=report_type),
             'No. Fees': agent.get_number_of_sales('Fee', client_type=report_type),
             'No. Services': agent.get_number_of_sales('Service', client_type=report_type),
             'Referrals': agent.get_referrals(client_type=report_type),
             # 'Extra Referrals': agent.get_no_extra_referrals(),
             'Ref/Sale': agent.ref_sales_ratio(client_type=report_type),
             # 'Total Ref/Sale': agent.total_ref_sales_ratio(),  # TODO: Get clarification
             '>14 months': agent.get_sub_gt_14months(client_type=report_type),
             'Yearly 12-14 months': agent.get_number_of_sub_for_range(12, 14, client_type=report_type),
             'Seasonal 6-11 months': agent.get_number_of_sub_for_range(6, 11, client_type=report_type),
             'Trim. 3-5 months': agent.get_number_of_sub_for_range(3, 5, client_type=report_type),
             'Monthly 1-2 months': agent.get_number_of_sub_for_range(1, 2, client_type=report_type),
             'Other': 0,  # TODO: Get clarification
             'Total Months': agent.get_all_total_sub_months(client_type=report_type),
             'Average Month': agent.get_average_month(client_type=report_type),
             'Average Membership Sale': agent.get_average_membership_sale(client_type=report_type),
             'Outcome % Scheduled work': agent.get_percentage_scheduled_work(client_type=report_type),  # TODO: Get clarification
             'agent': agent.get_full_name_or_username()
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
             'Extra Referrals': agent.get_no_extra_referrals(),
             'Ref/Sale': agent.ref_sales_ratio(),
             'Total Ref/Sale': agent.total_ref_sales_ratio(), # TODO: Get clarification
             '>14 months': agent.get_sub_gt_14months(),
             'Yearly 12-14 months': agent.get_number_of_sub_for_range(12, 14),
             'Seasonal 6-11 months': agent.get_number_of_sub_for_range(6, 11),
             'Trim. 3-5 months': agent.get_number_of_sub_for_range(3, 5),
             'Monthly 1-2 months': agent.get_number_of_sub_for_range(1, 2),
             'Other': 0, # TODO: Get clarification
             'Total Months': agent.get_all_total_sub_months(),
             'Average Month': agent.get_average_month(),
             'Average Membership Sale': agent.get_average_membership_sale(),
             'Outcome % Scheduled work': agent.get_percentage_scheduled_work(), # TODO: Get clarification
             'agent': agent.get_full_name_or_username()
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


def generate_actions_report(qs, user_actions):
    # df = pd.DataFrame.from_records(qs.values_list())
    # df.columns = [col for col in qs[0].__dict__.keys()][1:]

    # create empty dataframe with category and actions as columns and index
    columns = [x[0] for x in Action.CATEGORY_CHOICES]
    my_index = [x[0] for x in Action.ACTION_CHOICES]

    actions_df = pd.DataFrame(columns=columns, index=my_index)
    if not qs.exists():
        return actions_df

    for category, action in itertools.product(columns, my_index):
        actions_qs = qs.filter(action=action, category=category)
        total_amount = actions_qs.aggregate(total=Sum('amount'))['total']
        if total_amount is not None:
            actions_df.at[action, category] = total_amount
    if user_actions == 'global':
        actions_df.index.name = 'Total'
    else:
        actions_df.index.name = qs[0].agent.get_full_name_or_username()
    return actions_df


def generate_budget_table(qs: Union[QuerySet, List[Budget]], club: Club):
    end_date = timezone.now().date()
    start_date = years_ago(1).date()#.replace(day=1)

    month_list = pd.date_range(start_date, end_date, freq='MS').to_pydatetime().tolist()
    working_day_list = [qs.filter(month__year=x.year, month__month=x.month).aggregate(total=Avg('working_days'))['total'] for x in month_list]
    working_day_df = pd.DataFrame([working_day_list], columns=month_list, index=['working days'])

    users_index = [agent.get_full_name_or_username() for agent in club.user_set.all()]

    budget_df = pd.DataFrame(columns=month_list, index=users_index)

    for month, user in itertools.product(month_list, users_index):
        budget_amount = qs.filter(month__year=month.year, month__month=month.month, agent__username=user).aggregate(total=Sum('amount'))['total']
        budget_df.at[user, month] = budget_amount

    budget_df = budget_df.append(budget_df.sum().rename('Total'))

    new_df = pd.concat([working_day_df, budget_df])

    return new_df


def get_yesterday_progress(club):
    yesterday = timezone.now() - datetime.timedelta(days=1)
    agents = club.user_set.all()

    return [{
        'agent': agent.get_full_name_or_username(),
        'budget': agent.get_days_budget(yesterday),
        'budget_progress': agent.get_budget_progress(start_date=yesterday),
        'current_sales': agent.get_current_sales(start_date=yesterday),
        'gap': agent.get_current_sales(start_date=yesterday) - agent.get_budget_progress(start_date=yesterday),
        'trend': agent.get_trend(start_date=yesterday)
    } for agent in agents]


def get_month_progress(club):
    current_day = timezone.now().date()
    start_date = current_day.replace(day=1)

    end_date = datetime.date(
        current_day.year, current_day.month, calendar.monthrange(current_day.year, current_day.month)[-1]
    )# + datetime.timedelta(days=1)
    agents = club.user_set.all()

    return [{
        'agent': agent.get_full_name_or_username(),
        'budget': agent.get_budget_for_range(start_date),
        'budget_progress': agent.get_budget_progress(start_date=start_date, end_date=end_date),
        'current_sales': agent.get_current_sales(start_date=start_date, end_date=end_date),
        'gap': agent.get_current_sales(start_date=start_date, end_date=end_date) - agent.get_budget_progress(start_date=start_date, end_date=end_date),
        'trend': agent.get_trend(start_date=start_date, end_date=end_date)
    } for agent in agents]


def get_year_progress(club):
    current_day = timezone.now().date()
    start_date = years_ago(1).date()

    end_date = current_day
    # print(start_date, end_date)

    agents = club.user_set.all()

    return [{
        'agent': agent.get_full_name_or_username(),
        'budget': agent.get_budget_for_range(start_date, end_date=end_date),
        'budget_progress': agent.get_budget_progress(start_date=start_date, end_date=end_date),
        'current_sales': agent.get_current_sales(start_date=start_date, end_date=end_date),
        'gap': agent.get_current_sales(start_date=start_date, end_date=end_date) - agent.get_budget_progress(
            start_date=start_date, end_date=end_date),
        'trend': agent.get_trend(start_date=start_date, end_date=end_date)
    } for agent in agents]


def club_yesterday(club):
    yesterday = timezone.now() - datetime.timedelta(days=1)
    return {
        'budget': club.get_days_budget(yesterday),
        'budget_progress': club.get_budget_progress(start_date=yesterday),
        'current_sales': club.get_current_sales(start_date=yesterday),
        'gap': club.get_current_sales(start_date=yesterday) - club.get_budget_progress(start_date=yesterday),
        'trend': club.get_trend(start_date=yesterday)
    }


def club_month_progress(club):
    current_day = timezone.now().date()
    # first day of the current month
    start_date = current_day.replace(day=1)

    # last day of the current month
    end_date = datetime.date(
        current_day.year, current_day.month, calendar.monthrange(current_day.year, current_day.month)[-1]
    )

    return {
        'budget': club.get_budget_for_range(start_date),
        'budget_progress': club.get_budget_progress(start_date=start_date, end_date=end_date),
        'current_sales': club.get_current_sales(start_date=start_date, end_date=end_date),
        'gap': club.get_current_sales(start_date=start_date, end_date=end_date) - club.get_budget_progress(start_date=start_date, end_date=end_date),
        'trend': club.get_trend(start_date=start_date, end_date=end_date)
    }


def club_year_progress(club):
    current_day = timezone.now().date()
    start_date = years_ago(1).date()

    end_date = current_day

    return {
        'budget': club.get_budget_for_range(start_date, end_date=end_date),
        'budget_progress': club.get_budget_progress(start_date=start_date, end_date=end_date),
        'current_sales': club.get_current_sales(start_date=start_date, end_date=end_date),
        'gap': club.get_current_sales(start_date=start_date, end_date=end_date) - club.get_budget_progress(
            start_date=start_date, end_date=end_date),
        'trend': club.get_trend(start_date=start_date, end_date=end_date)
    }


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
