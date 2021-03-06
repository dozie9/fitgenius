from django.contrib import admin

from .models import (Club, Product, Budget, OfferedItem, Offer, Action, WorkingHour)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title']
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['club', 'agent', 'amount', 'month']


@admin.register(OfferedItem)
class OfferedItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'number_of_months']


class OfferedItemInline(admin.TabularInline):
    model = OfferedItem


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['client_type', 'agent', 'date', 'meeting_type', 'category', 'accepted', 'referrals']
    inlines = [OfferedItemInline]


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'time_spent', 'date', 'action', 'category']


@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    list_display = ['agent', 'date', 'hours']
