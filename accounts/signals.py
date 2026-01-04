from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_profile_and_welcome(sender, instance, created, **kwargs):
    if not created:
        return

    Profile.objects.get_or_create(user=instance, defaults={"role": "buyer"})

    try:
        send_mail(
            subject="Welcome to CommerceGrid 🎉",
            message=f"Hi {instance.username}, welcome to CommerceGrid!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=True,   # 🔑 IMPORTANT
        )
    except Exception as e:
        logger.error(f"Welcome email failed: {e}")


@receiver(pre_save, sender=Profile)
def send_verification_email(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_profile = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return

    if old_profile.verification_status != "approved" and instance.verification_status == "approved":
        try:
            send_mail(
                subject="🎉 Seller Verified",
                message="Your seller account has been approved.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=True,  # 🔑 IMPORTANT
            )
        except Exception as e:
            logger.error(f"Verification email failed: {e}")
