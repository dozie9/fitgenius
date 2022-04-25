from django.urls import path
from django.views.generic import TemplateView

from fitgenius.core.views import DashboardView

app_name = "core"

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('auth-logout/', TemplateView.as_view(template_name="account/logout-success.html"), name='pages-logout'),
]
