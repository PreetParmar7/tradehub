from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from .emails import send_welcome_email


@receiver(post_save, sender=User)
def create_profile_and_welcome(sender, instance, created, **kwargs):
    if not created:
        return

    Profile.objects.create(user=instance, role='buyer')
    try:
        send_welcome_email(instance)
    except Exception as e:
        print("Email failed:", e)
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile

@receiver(pre_save, sender=Profile)
def send_verification_email(sender, instance, **kwargs):
    if not instance.pk:
        return  # new profile, skip

    old_profile = Profile.objects.get(pk=instance.pk)

    # ✅ Send email ONLY when status changes to approved
    if (
        old_profile.verification_status != 'approved'
        and instance.verification_status == 'approved'
    ):
        send_mail(
            subject="🎉 CommerceGrid – Seller Verified",
            message=f"""
Hi {instance.user.username},

Congratulations! 🎉

Your seller account has been successfully VERIFIED on CommerceGrid.

You can now:
✔ Add products
✔ Receive enquiries
✔ Appear higher in search results

Welcome to verified sellers community!

– CommerceGrid Team
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[instance.user.email],
        )
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

