from django.db.models import Avg, Count, Q
from django.utils import timezone
from leads.models import Lead
from leads.models import Lead
from django.db.models import Avg

from leads.models import Lead
from django.utils.timezone import now
from leads.models import Lead

from leads.models import Lead

from leads.models import Lead

def seller_response_metrics(user):
    leads = Lead.objects.filter(seller=user)
    total_leads = leads.count()

    responded_leads = leads.filter(
        status__in=['contacted', 'interested', 'not_interested', 'call_later']
    ).count()

    response_rate = (
        int((responded_leads / total_leads) * 100)
        if total_leads > 0 else 0
    )

    last_lead = leads.order_by('-created_at').first()

    return {
        "total_leads": total_leads,
        "responded_leads": responded_leads,
        "response_rate": response_rate,
        "last_active": last_lead.created_at if last_lead else None,
    }

def is_trusted_seller(user):
    metrics = seller_response_metrics(user)

    return (
        user.profile.is_verified and
        metrics['total_leads'] >= 10 and
        metrics['response_rate'] >= 80
    )
from reviews.models import Review
from django.utils import timezone
from datetime import timedelta

from django.db.models import Avg
from reviews.models import Review
from django.utils import timezone
from datetime import timedelta

from accounts.models import Profile

def seller_rank_score(user):
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return 0   # 👈 SAFE DEFAULT SCORE

    score = 0

    # Example scoring logic (keep yours if different)
    if profile.is_verified:
        score += 30

    score += profile.experience_years * 2

    return score
