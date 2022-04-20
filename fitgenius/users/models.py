from django.contrib.auth.models import AbstractUser
from django.db.models import (CharField, ForeignKey, CASCADE)
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for FitGenius.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    # name = CharField(_("Name of User"), blank=True, max_length=255)
    # first_name = None  # type: ignore
    last_name = CharField(_("Surname"), blank=True, max_length=255)

    MANAGER = 'manager'
    AGENT = 'agent'

    ROLES = (
        (MANAGER, MANAGER.title()),
        (AGENT, AGENT.title()),
    )

    user_type = CharField(_("Role"), choices=ROLES, max_length=255, null=True)
    club = ForeignKey('club.Club', on_delete=CASCADE, null=True)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
