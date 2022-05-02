from django import forms
from django.forms.widgets import TextInput

from .models import Action, Budget, Product, Offer, OfferedItem


class DateInput(TextInput):
    input_type = 'date'


class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ['action', 'category', 'amount', 'date']
        widgets = {
            'date': DateInput()
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['client_type', 'meeting_type', 'category', 'date', 'accepted', 'referrals']
        widgets = {
            'date': DateInput()
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['agent', 'amount', 'month', 'working_days']
        widgets = {
            'month': DateInput()
        }
