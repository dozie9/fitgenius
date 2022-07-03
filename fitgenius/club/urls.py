from django.urls import path

from .views import (
    CreateActionView, UpdateActionView, ListActionView, BudgetCreateView, BudgetUpdateView, BudgetListView,
    # ProductUpdateView, ProductListView, ProductCreateView, DeleteProductView,
    OfferCreateView, OfferUpdateView, OfferListView, DeleteActionView, DeleteBudgetView,
    DeleteOfferView, OfferedItemUpdateFormView, OfferedItemCreateFormView, OfferedItemView,
    DeleteOfferedItemView, OfferList, OfferPartialUpdateView, BudgetSalesView, SetWorkingHoursView, ReportView,
    ActionList
)

app_name = "club"

urlpatterns = [
    path('action/add/', CreateActionView.as_view(), name='add-action'),
    path('action/update/<int:pk>/', UpdateActionView.as_view(), name='update-action'),
    path('action/delete/<int:pk>/', DeleteActionView.as_view(), name='delete-action'),
    path('actions/', ListActionView.as_view(), name='list-action'),
    path('action/partial/', ActionList.as_view(), name='partial-list-action'),

    path('budget/add/', BudgetCreateView.as_view(), name='add-budget'),
    path('budget/update/<int:pk>/', BudgetUpdateView.as_view(), name='update-budget'),
    path('budget/delete/<int:pk>/', DeleteBudgetView.as_view(), name='delete-budget'),
    path('budgets/', BudgetListView.as_view(), name='list-budget'),

    # path('product/add/', ProductCreateView.as_view(), name='add-product'),
    # path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='update-product'),
    # path('product/delete/<int:pk>/', DeleteProductView.as_view(), name='delete-product'),
    # path('products/', ProductListView.as_view(), name='list-product'),

    path('offer/add/', OfferCreateView.as_view(), name='add-offer'),
    path('offer/update/<int:pk>/', OfferUpdateView.as_view(), name='update-offer'),
    path('offer/update/pairtial/<int:pk>/', OfferPartialUpdateView.as_view(), name='partial-update-offer'),
    path('offer/delete/<int:pk>/', DeleteOfferView.as_view(), name='delete-offer'),
    path('offers/', OfferListView.as_view(), name='list-offer'),
    path('offers/partial/', OfferList.as_view(), name='partial-list-offer'),

    path('htmx/offered_item-form/create/', OfferedItemCreateFormView.as_view(), name='create-offered_item-form'),
    path('htmx/offered_item-form/<int:pk>/', OfferedItemUpdateFormView.as_view(), name='offered_item-form'),
    path('htmx/offered_item-form/delete/<int:pk>/', DeleteOfferedItemView.as_view(), name='offered_item-delete'),
    path('offered-item/', OfferedItemView.as_view()),

    path('b-sales/', BudgetSalesView.as_view(), name='budget-sales'),

    path('set-working-hours/', SetWorkingHoursView.as_view(), name='set-working-hours'),

    path('report/', ReportView.as_view(), name='report')

]
