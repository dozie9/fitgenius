import json
from decimal import Decimal, DivisionByZero, DivisionUndefined, InvalidOperation

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Avg
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, RedirectView

from fitgenius.club.models import Offer
# from fitgenius.club.utils import agent_sales
from fitgenius.club.utils import (month_sale_vs_budget, product_totals, product_sale_by_month)
from fitgenius.utils.utils import DecimalEncoder

User = get_user_model()


class DashboardView(LoginRequiredMixin, TemplateView):
    # template_name = 'dashboard/dashboard.html'

    def get_template_names(self):
        if self.request.user.user_type == User.MANAGER:
            return ['dashboard/manager_dashboard.html']
        if self.request.user.user_type == User.AGENT:
            return ['dashboard/agent_dashboard.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent_uuid = self.request.user.uuid
        sales = Offer.objects.agent_sales(agent_uuid).filter(accepted=True)

        now = timezone.now()

        this_month_sales, this_month_budget = month_sale_vs_budget(agent_uuid, now.year, now.month)

        try:
            percent_budget_reached = (this_month_sales/Decimal(this_month_budget)) * 100
        except (ZeroDivisionError, DivisionByZero, InvalidOperation):
            percent_budget_reached = 0

        product_aggr = product_totals(agent_uuid)
        product_by_month = product_sale_by_month(agent_uuid)
        # print(product_aggr, json.dumps(product_aggr, cls=DecimalEncoder))

        sales_aggr = {
            'no_of_products': sales.aggregate(total_product=Sum('no_product'))['total_product'],
            'avg_sales': sales.aggregate(avg_sales=Avg('total_sales'))['avg_sales'],
            'total_sales': sales.aggregate(sales=Sum('total_sales'))['sales'],
            'percent_budget_reached': percent_budget_reached,
            'product_aggr_json': json.dumps(product_aggr, cls=DecimalEncoder),
            'product_by_month': json.dumps(product_by_month, default=str),
            'this_month_sales': this_month_sales

        }

        if self.request.user.user_type == User.MANAGER:
            pass

        context.update({
            'sales_aggr': sales_aggr,
            'sales': sales
        })
        return context


class HomeRedirectView(RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("core:dashboard")
