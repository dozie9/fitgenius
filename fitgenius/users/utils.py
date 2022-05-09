# from allauth.account.app_settings import app_settings
from allauth.account import app_settings
from allauth.account.forms import SignupForm
from allauth.account.utils import complete_signup, passthrough_next_redirect_url, get_next_redirect_url
from allauth.account.views import sensitive_post_parameters_m
from allauth.decorators import rate_limit
from allauth.exceptions import ImmediateHttpResponse
from allauth.utils import get_request_param, get_form_class
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView


class SignupView(

    FormView,
):
    # template_name = "account/signup." + app_settings.TEMPLATE_EXTENSION
    form_class = SignupForm
    redirect_field_name = "next"
    success_url = None

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super(SignupView, self).dispatch(request, *args, **kwargs)

    # def get_form_class(self):
    #     return get_form_class(app_settings.FORMS, "signup", self.form_class)

    # def get_success_url(self):
    #     # Explicitly passed ?next= URL takes precedence
    #     ret = (
    #         get_next_redirect_url(self.request, self.redirect_field_name)
    #         or self.success_url
    #     )
    #     return ret

    def form_valid(self, form):
        # By assigning the User to a property on the view, we allow subclasses
        # of SignupView to access the newly created User instance
        self.user = form.save(self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(SignupView, self).get_context_data(**kwargs)
        form = ret["form"]
        email = self.request.session.get("account_verified_email")
        if email:
            email_keys = ["email"]
            if app_settings.SIGNUP_EMAIL_ENTER_TWICE:
                email_keys.append("email2")
            for email_key in email_keys:
                form.fields[email_key].initial = email
        login_url = passthrough_next_redirect_url(
            self.request, reverse("account_login"), self.redirect_field_name
        )
        redirect_field_name = self.redirect_field_name
        site = get_current_site(self.request)
        redirect_field_value = get_request_param(self.request, redirect_field_name)
        ret.update(
            {
                "login_url": login_url,
                "redirect_field_name": redirect_field_name,
                "redirect_field_value": redirect_field_value,
                "site": site,
            }
        )
        return ret
