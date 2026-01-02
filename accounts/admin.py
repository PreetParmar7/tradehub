# accounts/admin.py

from django.contrib import admin
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .models import SellerVerification
# accounts/admin.py

from django.contrib import admin
from .models import Profile, SellerVerification

@admin.register(SellerVerification)
class SellerVerificationAdmin(admin.ModelAdmin):
    list_display = ("seller", "status", "submitted_at", "reviewed_at")
    list_filter = ("status",)
    actions = ["approve_verifications"]

    def approve_verifications(self, request, queryset):
        for verification in queryset:
            # ✅ Update verification
            verification.status = "approved"
            verification.reviewed_at = timezone.now()
            verification.save()

            # ✅ VERY IMPORTANT: Update Profile
            profile = verification.seller.profile
            profile.verification_status = "approved"
            profile.is_verified = True
            profile.save()

            # 📧 Approval email
            send_mail(
                subject="🎉 Your Trade seller account is approved",
                message=(
                    f"Hi {verification.seller.username},\n\n"
                    "Your seller verification has been approved.\n"
                    "You can now access your seller dashboard and start selling.\n\n"
                    "– CommerceGrid Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[verification.seller.email],
                fail_silently=False,
            )

    approve_verifications.short_description = "Approve selected seller verifications"
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "verification_status",
        "is_verified",
        "city",
        "state",
        "phone",
    )

    list_filter = ("role", "verification_status", "state")
    search_fields = ("user__username", "phone", "business_name")

    readonly_fields = ("created_at",)

    fieldsets = (
        ("User Info", {
            "fields": ("user", "role", "phone")
        }),
        ("Business Info", {
            "fields": (
                "business_name",
                "about",
                "city",
                "state",
                "pincode",
                "experience_years",
            )
        }),
        ("Verification", {
            "fields": (
                "verification_status",
                "is_verified",
            )
        }),
        ("Meta", {
            "fields": ("created_at",)
        }),
    )
