from django.urls import path

from .views import (CreateActionView, UpdateActionView, ListActionView, BudgetCreateView, BudgetUpdateView,
                    BudgetListView, ProductUpdateView, ProductListView, ProductCreateView, OfferCreateView,
                    OfferUpdateView, OfferListView, DeleteActionView)

app_name = "club"

urlpatterns = [
    path('action/add/', CreateActionView.as_view(), name='add-action'),
    path('action/update/<int:pk>/', UpdateActionView.as_view(), name='update-action'),
    path('action/delete/<int:pk>/', DeleteActionView.as_view(), name='delete-action'),
    path('actions/', ListActionView.as_view(), name='list-action'),

    path('budget/add/', BudgetCreateView.as_view(), name='add-budget'),
    path('budget/update/<int:pk>/', BudgetUpdateView.as_view(), name='update-budget'),
    path('budgets/', BudgetListView.as_view(), name='list-budget'),

    path('product/add/', ProductCreateView.as_view(), name='add-budget'),
    path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='update-product'),
    path('products/', ProductListView.as_view(), name='list-product'),

    path('offer/add/', OfferCreateView.as_view(), name='add-offer'),
    path('offer/update/<int:pk>/', OfferUpdateView.as_view(), name='update-offer'),
    path('offers/', OfferListView.as_view(), name='list-offer'),
]
