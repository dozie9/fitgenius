from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, BaseCreateView, DeleteView
from django.views.generic.list import ListView

from .models import Action, Budget, Product, Offer


class CreateActionView(LoginRequiredMixin, CreateView):
    model = Action
    template_name = 'club/actions-form.html'
    fields = ['action', 'category', 'amount', 'date']
    success_url = reverse_lazy('club:list-action')

    def form_valid(self, form, *args, **kwargs):
        # form = super(CreateActionView, self).form_valid(*args, **kwargs)
        form.instance.agent = self.request.user
        return super().form_valid(form, *args, **kwargs)


class AjaxTemplateMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'ajax_template_name'):
            split = self.template_name.split('.html')
            split[-1] = '_inner'
            split.append('.html')
            self.ajax_template_name = ''.join(split)
        if request.is_ajax():
            self.template_name = self.ajax_template_name
        return super().dispatch(request, *args, **kwargs)


class UpdateActionView(LoginRequiredMixin, AjaxTemplateMixin, UpdateView):
    model = Action
    template_name = 'club/actions-form.html'
    fields = ['action', 'category', 'amount', 'date']
    success_url = reverse_lazy('club:list-action')


class DeleteActionView(LoginRequiredMixin, DeleteView):
    model = Action
    success_message = 'Successfully deleted'
    success_url = reverse_lazy('club:list-action')


class ListActionView(LoginRequiredMixin, BaseCreateView, ListView):
    model = Action
    template_name = 'club/actions-list.html'
    fields = ['action', 'category', 'amount', 'date']
    success_url = reverse_lazy('club:list-action')

    def form_valid(self, form, *args, **kwargs):
        # form = super(CreateActionView, self).form_valid(*args, **kwargs)
        form.instance.agent = self.request.user
        return super().form_valid(form, *args, **kwargs)


class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    template_name = 'club/budget-form.html'
    fields = ['agent', 'amount', 'month']
    success_url = '/'

    # def form_valid(self, form, *args, **kwargs):
    #
    #     form.instance.agent = self.request.user
    #     return super().form_valid(form, *args, **kwargs)


class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    template_name = 'club/budget-form.html'
    fields = ['agent', 'amount', 'month']
    success_url = '/'


class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'club/budget-list.html'


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'club/product-form.html'
    fields = ['title', 'value']
    success_url = '/'


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'club/product-form.html'
    fields = ['title', 'value']
    success_url = '/'


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'club/product-list.html'


class OfferCreateView(LoginRequiredMixin, CreateView):
    model = Offer
    template_name = 'club/offer-form.html'
    fields = ['agent', 'offered_items', 'meeting_type', 'category', 'date', 'accepted', 'referrals']
    success_url = '/'


class OfferUpdateView(LoginRequiredMixin, UpdateView):
    model = Offer
    template_name = 'club/offer-form.html'
    fields = ['agent', 'offered_items', 'meeting_type', 'category', 'date', 'accepted', 'referrals']
    success_url = '/'


class OfferListView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'club/offer-list.html'
