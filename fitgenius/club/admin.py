from django.contrib import admin

from .models import Club, Product, Budget, OfferedItem, Offer, Action


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'value', 'club']


@admin.register(Budget)
class BudjectAdmin(admin.ModelAdmin):
    list_display = ['club', 'agent', 'month']


@admin.register(OfferedItem)
class OfferedItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'number_of_months']


class OfferedItemInline(admin.TabularInline):
    model = OfferedItem


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['client_type', 'agent', 'date', 'meeting_type', 'category', 'accepted', 'referrals']
    inlines = [OfferedItemInline]


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'time_spent', 'date', 'amount', 'action', 'category']
