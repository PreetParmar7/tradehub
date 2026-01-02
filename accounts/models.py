from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):

    STATE_CHOICES = [
        ('AN', 'Andaman & Nicobar'),
        ('AP', 'Andhra Pradesh'),
        ('AR', 'Arunachal Pradesh'),
        ('AS', 'Assam'),
        ('BR', 'Bihar'),
        ('CG', 'Chhattisgarh'),
        ('DL', 'Delhi'),
        ('GA', 'Goa'),
        ('GJ', 'Gujarat'),
        ('HR', 'Haryana'),
        ('HP', 'Himachal Pradesh'),
        ('JH', 'Jharkhand'),
        ('KA', 'Karnataka'),
        ('KL', 'Kerala'),
        ('MP', 'Madhya Pradesh'),
        ('MH', 'Maharashtra'),
        ('OR', 'Odisha'),
        ('PB', 'Punjab'),
        ('RJ', 'Rajasthan'),
        ('TN', 'Tamil Nadu'),
        ('TS', 'Telangana'),
        ('UP', 'Uttar Pradesh'),
        ('UK', 'Uttarakhand'),
        ('WB', 'West Bengal'),
    ]

    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('both', 'Buyer & Seller'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    phone = models.CharField(max_length=15, blank=True)

    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=5, choices=STATE_CHOICES, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    business_name = models.CharField(max_length=200, blank=True)
    about = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)

    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.is_verified = self.verification_status == 'approved'
        super().save(*args, **kwargs)

class SellerVerification(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    seller = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='seller_verification'
    )

    # 🏢 BUSINESS DETAILS
    business_name = models.CharField(max_length=200)
    gst_number = models.CharField(max_length=50, blank=True)

    # 📄 DOCUMENTS
    id_proof = models.FileField(upload_to='verification/id_proofs/')
    gst_certificate = models.FileField(upload_to='verification/gst_certificate/',blank=True,null=True)

    # 🔁 VERIFICATION FLOW
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    admin_remarks = models.TextField(blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.username} - {self.status}"

    def mark_submitted(self):
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()

    def approve(self):
        """
        🔥 SINGLE PLACE WHERE APPROVAL HAPPENS
        """
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        self.save()

        profile = self.seller.profile
        profile.verification_status = 'approved'
        profile.save()

    def reject(self, remarks=""):
        self.status = 'rejected'
        self.admin_remarks = remarks
        self.reviewed_at = timezone.now()
        self.save()

        profile = self.seller.profile
        profile.verification_status = 'rejected'
        profile.save()
