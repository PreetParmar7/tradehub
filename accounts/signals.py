from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from threading import Thread

from .models import Profile
from .emails import send_welcome_email


# ======================================================
# ASYNC HELPERS (CRITICAL FOR RAILWAY)
# ======================================================

def send_async_welcome_email(user):
    try:
        send_welcome_email(user)
    except Exception as e:
        print("Welcome email failed:", e)


def send_async_verification_email(profile):
    try:
        send_mail(
            subject="🎉 CommerceGrid – Seller Verified",
            message=f"""
Hi {profile.user.username},

Congratulations! 🎉

Your seller account has been successfully VERIFIED on CommerceGrid.

You can now:
✔ Add products
✔ Receive enquiries
✔ Appear higher in search results

Welcome to the verified sellers community!

– CommerceGrid Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile.user.email],
            fail_silently=True,
        )
    except Exception as e:
        print("Verification email failed:", e)


# ======================================================
# CREATE PROFILE + WELCOME EMAIL (POST SAVE USER)
# ======================================================

@receiver(post_save, sender=User)
def create_profile_and_welcome(sender, instance, created, **kwargs):
    if not created:
        return

    # Create profile
    Profile.objects.create(user=instance, role="buyer")

    # Send welcome email ASYNC (NON-BLOCKING)
    Thread(
        target=send_async_welcome_email,
        args=(instance,),
        daemon=True
    ).start()


# ======================================================
# SELLER VERIFICATION EMAIL (PRE SAVE PROFILE)
# ======================================================

@receiver(pre_save, sender=Profile)
def send_verification_email(sender, instance, **kwargs):
    if not instance.pk:
        return  # new profile, skip

    try:
        old_profile = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return

    # Send email ONLY when status changes to approved
    if (
        old_profile.verification_status != "approved"
        and instance.verification_status == "approved"
    ):
        Thread(
            target=send_async_verification_email,
            args=(instance,),
            daemon=True
        ).start()
