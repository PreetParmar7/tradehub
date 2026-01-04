from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if not created:
        return

    Profile.objects.get_or_create(
        user=instance,
        defaults={"role": "buyer"}
    )

    # SAFE email send
    try:
        from .emails import send_welcome_email
        send_welcome_email(instance)
    except Exception as e:
        logger.error(f"Welcome email failed: {e}")


@receiver(pre_save, sender=Profile)
def send_verification_email(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return

    if old.verification_status != "approved" and instance.verification_status == "approved":
        try:
            send_mail(
                subject="🎉 CommerceGrid – Seller Verified",
                message=f"""
Hi {instance.user.username},

Your seller account has been VERIFIED.

You can now add products and receive orders.

– CommerceGrid Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=True,  # 🔥 IMPORTANT
            )
        except Exception as e:
            logger.error(f"Verification email failed: {e}")
