from django import forms
from django.contrib.auth import get_user_model
from django.forms.widgets import TextInput
# from tempus_dominus.widgets import DatePicker

from .models import Action, Budget, Product, Offer, OfferedItem


User = get_user_model()


class DateInput(TextInput):
    input_type = 'date'


class MonthInput(TextInput):
    input_type = 'month'


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
    # month = MonthField()
    class Meta:
        model = Budget
        fields = ['agent', 'amount', 'month', 'working_days']
        widgets = {
            'month': TextInput(attrs={
                'class': 'picker',
                'readonly': True
            })
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)

        super().__init__(*args, **kwargs)

        self.fields['agent'].queryset = User.objects.filter(club=request.user.club)
