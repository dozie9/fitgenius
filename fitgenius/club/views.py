from allauth.account.views import SignupView
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, BaseCreateView, DeleteView, FormView
from django.views.generic.list import ListView
from guardian.mixins import PermissionListMixin, PermissionRequiredMixin

from .forms import ActionForm, OfferForm, BudgetForm
from .models import Action, Budget, Product, Offer, OfferedItem
from ..users.forms import UserSignupForm
from ..utils.utils import PortalRestrictionMixin

User = get_user_model()


class CreateActionView(LoginRequiredMixin, CreateView):
    model = Action
    template_name = 'club/actions-form.html'
    # fields = ['action', 'category', 'amount', 'date']
    form_class = ActionForm
    success_url = reverse_lazy('club:list-action')

    def form_valid(self, form, *args, **kwargs):
        # form = super(CreateActionView, self).form_valid(*args, **kwargs)
        form.instance.agent = self.request.user
        form.instance.club = self.request.user.club
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


class UpdateActionView(LoginRequiredMixin, PermissionRequiredMixin, AjaxTemplateMixin, UpdateView):
    model = Action
    template_name = 'club/actions-form.html'
    # fields = ['action', 'category', 'amount', 'date']
    form_class = ActionForm
    success_url = reverse_lazy('club:list-action')
    permission_required = ['club.access_action']
    raise_exception = True


class DeleteActionView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Action
    success_message = 'Successfully deleted'
    success_url = reverse_lazy('club:list-action')
    permission_required = ['club.access_action']
    raise_exception = True


class ListActionView(LoginRequiredMixin, PermissionListMixin, BaseCreateView, ListView):
    model = Action
    template_name = 'club/actions-list.html'
    # fields = ['action', 'category', 'amount', 'date']
    form_class = ActionForm
    success_url = reverse_lazy('club:list-action')
    permission_required = ['club.access_action']
    raise_exception = True
    # get_objects_for_user_extra_kwargs = {'use_groups': False}

    def form_valid(self, form, *args, **kwargs):
        # form = super(CreateActionView, self).form_valid(*args, **kwargs)
        form.instance.agent = self.request.user
        form.instance.club = self.request.user.club
        return super().form_valid(form, *args, **kwargs)


class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    template_name = 'club/budget-form.html'
    # fields = ['agent', 'amount', 'month', 'working_days']
    form_class = BudgetForm
    success_url = reverse_lazy('club:list-budget')

    # def form_valid(self, form, *args, **kwargs):
    #
    #     form.instance.agent = self.request.user
    #     return super().form_valid(form, *args, **kwargs)


class BudgetUpdateView(LoginRequiredMixin, AjaxTemplateMixin, UpdateView):
    model = Budget
    template_name = 'club/budget-form.html'
    # fields = ['agent', 'amount', 'month', 'working_days']
    form_class = BudgetForm
    success_url = reverse_lazy('club:list-budget')


class BudgetListView(LoginRequiredMixin, BaseCreateView, ListView):
    model = Budget
    template_name = 'club/budget-list.html'
    # fields = ['agent', 'amount', 'month', 'working_days']
    form_class = BudgetForm
    success_url = reverse_lazy('club:list-budget')

    def form_valid(self, form, *args, **kwargs):
        # form = super(CreateActionView, self).form_valid(*args, **kwargs)
        form.instance.club = self.request.user.club
        return super().form_valid(form, *args, **kwargs)


class DeleteBudgetView(LoginRequiredMixin, DeleteView):
    model = Budget
    success_message = 'Successfully deleted'
    success_url = reverse_lazy('club:list-budget')


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'club/product-form.html'
    fields = ['title', 'value']
    success_url = reverse_lazy('club:list-product')

    def form_valid(self, form, *args, **kwargs):
        # form = super(CreateActionView, self).form_valid(*args, **kwargs)
        form.instance.club = self.request.user.club
        return super().form_valid(form, *args, **kwargs)


class ProductUpdateView(LoginRequiredMixin, AjaxTemplateMixin, UpdateView):
    model = Product
    template_name = 'club/product-form.html'
    fields = ['title', 'value']
    success_url = reverse_lazy('club:list-product')


class ProductListView(LoginRequiredMixin, BaseCreateView, ListView):
    model = Product
    template_name = 'club/product-list.html'
    fields = ['title', 'value']
    success_url = reverse_lazy('club:list-product')

    def form_valid(self, form, *args, **kwargs):
        # form = super(CreateActionView, self).form_valid(*args, **kwargs)
        form.instance.club = self.request.user.club
        return super().form_valid(form, *args, **kwargs)


class DeleteProductView(LoginRequiredMixin, DeleteView):
    model = Product
    success_message = 'Successfully deleted'
    success_url = reverse_lazy('club:list-product')


OfferedItemFormset = inlineformset_factory(
    Offer, OfferedItem, fields=('product', 'quantity', 'number_of_months')
)


class OfferItemCreateView(CreateView):
    template_name = 'club/offer_item-form.html'
    fields = ['product', 'quantity', 'number_of_months']
    success_url = reverse_lazy('')


class OfferCreateView(LoginRequiredMixin, CreateView):
    model = Offer
    template_name = 'club/offer-form.html'
    # fields = ['agent', 'meeting_type', 'category', 'date', 'accepted', 'referrals']
    form_class = OfferForm
    success_url = reverse_lazy('club:list-offer')

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'client_type': self.request.GET.get('client_type', default=None)
        })

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        offered_item_form = OfferedItemFormset()

        return self.render_to_response(
            self.get_context_data(
                form=form, offered_item_form=offered_item_form
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        offered_item_form = OfferedItemFormset(self.request.POST)

        if form.is_valid() and offered_item_form.is_valid():
            return self.form_valid(form, offered_item_form)
        else:
            return self.form_invalid(form, offered_item_form)

    def form_valid(self, form, offered_item_form):

        form.instance.agent = self.request.user
        self.object = form.save()
        offered_item_form.instance = self.object
        offered_item_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, offered_item_form):

        return self.render_to_response(
            self.get_context_data(
                form=form, offered_item_form=offered_item_form
            )
        )


class OfferedItemUpdateFormView(LoginRequiredMixin, UpdateView):
    template_name = 'club/partials/offered_item-form.html'
    model = OfferedItem
    fields = ['product', 'quantity', 'number_of_months']

    def get_success_url(self):
        messages.success(
            self.request,
            'Successfully submitted'
        )
        return reverse('club:offered_item-form', args=[self.object.id])


class OfferedItemCreateFormView(LoginRequiredMixin, CreateView):
    template_name = 'club/partials/offered_item-form.html'
    model = OfferedItem
    fields = ['product', 'quantity', 'number_of_months']

    def get_context_data(self, *args, **kwargs):
        # print(self.request.path, 'eeeeeeeeeeeeeeeeeee')
        ctx = super().get_context_data(*args, **kwargs)
        offer_item_id = self.request.GET.get('of')

        ctx.update({
            'offer_item_id': offer_item_id
        })
        return ctx

    def form_valid(self, form, *args, **kwargs):
        offer_item_id = self.request.GET.get('of')
        form.instance.offer_id = int(offer_item_id)
        return super().form_valid(form, *args, **kwargs)


    def get_success_url(self):
        messages.success(
            self.request,
            'Successfully submitted'
        )
        print(self.request.path)
        return reverse('club:offered_item-form', args=[self.object.id])


class DeleteOfferedItemView(LoginRequiredMixin, DeleteView):
    model = OfferedItem
    success_message = 'Successfully deleted'
    success_url = reverse_lazy('club:list-offer')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return HttpResponse('')


class OfferedItemView(TemplateView):
    template_name = 'club/offer-update-form.html'


class OfferPartialUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Offer
    template_name = 'club/partials/offer-form.html'
    # fields = ['agent', 'meeting_type', 'category', 'date', 'accepted', 'referrals']
    form_class = OfferForm
    success_url = reverse_lazy('club:list-offer')
    raise_exception = True
    permission_required = ['club.access_offer']


class OfferUpdateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxTemplateMixin, UpdateView):
    model = Offer
    template_name = 'club/offer-form.html'
    # fields = ['agent', 'meeting_type', 'category', 'date', 'accepted', 'referrals']
    form_class = OfferForm
    success_url = reverse_lazy('club:list-offer')
    permission_required = ['club.access_offer']
    raise_exception = True

    def form_valid(self, form, *args, **kwargs):

        response = super(OfferUpdateView, self).form_valid(form, *args, **kwargs)
        return HttpResponse(status=204, headers={'HX-Trigger': 'dataChanged'})


class OfferList(LoginRequiredMixin, PermissionListMixin, ListView):
    model = Offer
    template_name = 'club/partials/offer-list.html'
    permission_required = ['club.access_offer']
    raise_exception = True

    def get_queryset(self):
        queryset = super().get_queryset()

        client_type = self.request.GET.get('client_type', default=None)
        if not client_type:
            return queryset

        return queryset.filter(client_type=client_type)


class OfferListView(LoginRequiredMixin, PermissionListMixin, BaseCreateView, ListView):
    model = Offer
    template_name = 'club/offer-list.html'
    # fields = ['agent', 'meeting_type', 'category', 'date', 'accepted', 'referrals']
    form_class = OfferForm
    success_url = reverse_lazy('club:list-offer')
    permission_required = ['club.access_offer']
    raise_exception = True

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'client_type': self.request.GET.get('client_type', default=None)
        })
        return initial

    def get_queryset(self):
        queryset = super(OfferListView, self).get_queryset()

        client_type = self.request.GET.get('client_type', default=None)
        if not client_type:
            return queryset
        return queryset.filter(client_type=client_type)

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        offered_item_form = OfferedItemFormset()
        self.object_list = self.get_queryset()

        return self.render_to_response(
            self.get_context_data(
                form=form, offered_item_form=offered_item_form
            )
        )

    # def post(self, request, *args, **kwargs):
    #     self.object = None
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #     offered_item_form = OfferedItemFormset(self.request.POST)
    #
    #     if form.is_valid() and offered_item_form.is_valid():
    #         return self.form_valid(form, offered_item_form)
    #     else:
    #         return self.form_invalid(form, offered_item_form)

    # def form_valid(self, form, offered_item_form):
    #
    #     self.object = form.save()
    #     offered_item_form.instance = self.object
    #     offered_item_form.save()
    #     return HttpResponseRedirect(self.get_success_url())
    #
    # def form_invalid(self, form, offered_item_form):
    #
    #     return self.render_to_response(
    #         self.get_context_data(
    #             form=form, offered_item_form=offered_item_form
    #         )
    #     )


class DeleteOfferView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Offer
    success_message = 'Successfully deleted'
    success_url = reverse_lazy('club:list-offer')
    permission_required = ['club.access_offer']
    raise_exception = True
