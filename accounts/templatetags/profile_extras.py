from django import template
register = template.Library()

@register.filter
def get_profile(user):
    try:
        return user.profile
    except Exception:
        return None
