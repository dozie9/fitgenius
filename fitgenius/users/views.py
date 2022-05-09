from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView, ListView
from django.views.generic.edit import CreateView

from fitgenius.users.forms import UserSignupForm
from fitgenius.users.utils import SignupView
from fitgenius.utils.utils import PortalRestrictionMixin

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    fields = ["first_name", "last_name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert (
            self.request.user.is_authenticated
        )  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class CreateUserView(LoginRequiredMixin, SignupView, PortalRestrictionMixin):
    form_class = UserSignupForm
    template_name = 'users/user_form.html'
    # model = User

    def get_success_url(self):

        return reverse('users:update-user', args=[self.user.uuid or None])

    def form_valid(self, form):
        response = super().form_valid(form)
        self.user.club = self.request.user.club
        self.user.save()
        return HttpResponseRedirect(self.get_success_url())


class UpdateUserView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['email', 'user_type']
    slug_url_kwarg = 'uuid'
    template_name = 'users/user_form.html'
    query_pk_and_slug = False
    slug_field = 'uuid'


class ListUserView(LoginRequiredMixin, PortalRestrictionMixin, ListView):
    model = User
    template_name = 'users/user-list.html'

    def get_queryset(self):
        qs = super(ListUserView, self).get_queryset()
        return qs.filter(club=self.request.user.club)
