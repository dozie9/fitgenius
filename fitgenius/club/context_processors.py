from datetime import date

from django.contrib.auth import get_user_model

from .models import Action, Offer, WorkingHour

User = get_user_model()


def club_context(request):
    """Expose some settings from club in templates."""
    return {
        "ClubAction": Action,
        "ClubOffer": Offer,
    }


def has_working_hours(request):
    if request.user.is_anonymous or request.user.user_type == User.MANAGER or request.user.is_superuser:
        return {
            "has_working_hours": True
        }

    return {
        "has_working_hours": WorkingHour.objects.filter(date=date.today()).exists()
    }
