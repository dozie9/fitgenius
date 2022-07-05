from datetime import date

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Action, Offer, WorkingHour
from ..utils.utils import years_ago

User = get_user_model()


def club_context(request):
    """Expose some settings from club in templates."""
    a_year_ago = years_ago(1)
    return {
        "ClubAction": Action,
        "ClubOffer": Offer,
        'current_date': timezone.now().date(),
        'a_year_ago': a_year_ago,
    }


def has_working_hours(request):
    if request.user.is_anonymous or request.user.user_type == User.MANAGER or request.user.is_superuser:
        return {
            "has_working_hours": True
        }

    return {
        "has_working_hours": WorkingHour.objects.filter(date=date.today()).exists()
    }
