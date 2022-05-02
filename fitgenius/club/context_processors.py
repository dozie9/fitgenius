from .models import Action, Offer


def club_context(request):
    """Expose some settings from club in templates."""
    return {
        "ClubAction": Action,
        "ClubOffer": Offer,
    }
