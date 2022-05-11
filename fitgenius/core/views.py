from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'


class HomeRedirectView(RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("core:dashboard")
