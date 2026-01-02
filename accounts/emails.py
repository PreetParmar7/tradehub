from django.core.mail import send_mail
from django.conf import settings


def send_welcome_email(user):
    subject = "Welcome to CommerceGrid 🎉"

    if user.profile.role in ['seller', 'both']:
        message = f"""
Hi {user.username},

Welcome to CommerceGrid!

Your seller account has been created successfully.

Next steps:
1. Complete your dealer profile
2. Upload verification documents
3. Submit for verification

Once approved, you’ll be able to add products.

– CommerceGrid Team
"""
    else:
        message = f"""
Hi {user.username},

Welcome to CommerceGrid!

You can now explore trusted local sellers,
compare products, and place orders with confidence.

– CommerceGrid Team
"""

    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])


def send_verification_under_review_email(user):
    send_mail(
        "CommerceGrid – Verification Under Review",
        f"""
Hi {user.username},

Your verification documents have been received.

Our team is reviewing your details.
You will be notified once verification is complete.

– CommerceGrid Team
""",
        settings.EMAIL_HOST_USER,
        [user.email],
    )


def send_verification_approved_email(user):
    send_mail(
        "🎉 CommerceGrid – Seller Verification Approved",
        f"""
Hi {user.username},

Congratulations! 🎉

Your seller account has been VERIFIED.
You can now add products and access seller features.

– CommerceGrid Team
""",
        settings.EMAIL_HOST_USER,
        [user.email],
    )


def send_verification_rejected_email(user):
    send_mail(
        "CommerceGrid – Verification Rejected",
        f"""
Hi {user.username},

Your verification was rejected.

Please update your documents and submit again.

– CommerceGrid Team
""",
        settings.EMAIL_HOST_USER,
        [user.email],
    )
