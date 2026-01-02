from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Profile

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Profile

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")

        # ✅ PASSWORD MATCH CHECK
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("accounts:signup")

        # ✅ USERNAME EXISTS CHECK
        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Username already exists. Please choose a different username."
            )
            return redirect("accounts:signup")

        # ✅ EMAIL EXISTS CHECK
        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                "An account with this email already exists."
            )
            return redirect("accounts:signup")

        # ✅ CREATE USER
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # ✅ UPDATE EXISTING PROFILE (DO NOT CREATE)
        profile = user.profile
        profile.role = role
        profile.save()

        messages.success(
            request,
            "Account created successfully. Please login."
        )
        return redirect("accounts:login")

    return render(request, "accounts/signup.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('accounts:login')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('core:home')
from accounts.models import Profile

@login_required
def edit_dealer_profile(request):
    profile = request.user.profile

    if profile.role not in ["seller", "both"]:
        return redirect("core:home")

    if request.method == "POST":
        profile.business_name = request.POST.get("business_name")
        profile.about = request.POST.get("about")
        profile.experience_years = request.POST.get("experience_years")
        profile.phone = request.POST.get("phone")
        profile.city = request.POST.get("city")
        profile.state = request.POST.get("state")  # ✅ comes from dropdown

        if request.FILES.get("id_document"):
            profile.id_document = request.FILES.get("id_document")
            profile.verification_status = "pending"

        profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect("accounts:seller_dashboard")

    return render(request, "accounts/edit_dealer_profile.html", {
        "profile": profile,
        "state_choices": Profile.STATE_CHOICES,  # ✅ ADD THIS
    })

from django.contrib import messages
from .emails import send_verification_under_review_email
from django.core.mail import send_mail
from django.conf import settings
from products.models import Product
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from products.models import Product

@login_required
def seller_dashboard(request):
    profile = request.user.profile

    if profile.role not in ['seller', 'both']:
        return redirect('core:home')

    if profile.verification_status != 'approved':
        return redirect('accounts:seller_verification')

    products = Product.objects.filter(seller=request.user)

    return render(request, 'accounts/seller_dashboard.html', {
        'profile': profile,
        'products': products,
    })

from .models import SellerVerification
from django.utils import timezone

from .emails import send_verification_under_review_email
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from .models import SellerVerification
from .emails import send_verification_under_review_email


@login_required
def seller_verification(request):
    profile = request.user.profile

    # 🔒 Only sellers or both
    if profile.role not in ['seller', 'both']:
        return redirect('core:home')

    # ✅ Already approved
    if profile.verification_status == 'approved':
        return redirect('accounts:seller_dashboard')

    verification, created = SellerVerification.objects.get_or_create(
        seller=request.user
    )

    if request.method == 'POST':

        # ---------------------------
        # 🔴 REQUIRED PROFILE FIELDS
        # ---------------------------
        required_fields = {
            "phone": request.POST.get("phone"),
            "business_name": request.POST.get("business_name"),
            "city": request.POST.get("city"),
            "state": request.POST.get("state"),
            "pincode": request.POST.get("pincode"),
            "about": request.POST.get("about"),
        }

        missing_fields = [k for k, v in required_fields.items() if not v]

        if missing_fields:
            messages.error(
                request,
                "Please fill all required business details before submitting."
            )
            return redirect('accounts:seller_verification')

        # ---------------------------
        # ✅ SAVE VERIFICATION DATA
        # ---------------------------
        verification.business_name = request.POST.get('business_name')
        verification.gst_number = request.POST.get('gst_number')

        # ✅ Save files ONLY if uploaded (prevents wiping existing files)
        if request.FILES.get('id_proof'):
            verification.id_proof = request.FILES.get('id_proof')

        if request.FILES.get('gst_certificate'):
            verification.gst_certificate = request.FILES.get('gst_certificate')

        verification.status = 'under_review'
        verification.submitted_at = timezone.now()
        verification.save()

        # ---------------------------
        # ✅ SAVE PROFILE DATA
        # ---------------------------
        profile.phone = request.POST.get('phone')
        profile.business_name = request.POST.get('business_name')
        profile.city = request.POST.get('city')
        profile.state = request.POST.get('state')
        profile.pincode = request.POST.get('pincode')
        profile.about = request.POST.get('about')
        profile.verification_status = 'under_review'
        profile.save()

        # ---------------------------
        # 📧 EMAIL TO SELLER
        # ---------------------------
        send_verification_under_review_email(request.user)

        messages.success(
            request,
            "Verification submitted successfully. Our team will review your documents."
        )

        return redirect('accounts:seller_verification')

    return render(request, 'accounts/seller_verification.html', {
        'verification': verification,
        'profile': profile,   # ✅ REQUIRED
    })
