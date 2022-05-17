from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Avg
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView

from fitgenius.club.utils import agent_sales

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
        sales = agent_sales(self.request.user.uuid).filter(accepted=True)

        sales_aggr = {
            'no_of_products': sales.aggregate(total_product=Sum('no_product'))['total_product'],
            'avg_sales': sales.aggregate(avg_sales=Avg('total_sales'))['avg_sales'],
            'total_sales': sales.aggregate(sales=Sum('total_sales'))['sales']
        }
        context.update({
            'sales_aggr': sales_aggr,
            'sales': sales
        })
        return context


class HomeRedirectView(RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("core:dashboard")
