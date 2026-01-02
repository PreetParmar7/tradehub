# products/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from datetime import timedelta
from orders.models import Order

from .models import Product, Category, CategoryRequest
from analytics.models import ProductView, ProductAnalytics
from leads.models import Lead
from accounts.models import Profile
from accounts.utils import seller_rank_score, seller_response_metrics, is_trusted_seller
from django.contrib.auth.models import User
from reviews.models import Review
from django.db.models import Avg


# =========================
# 🛍 PRODUCT LIST
# =========================
def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    state_code = request.GET.get("state")
    state_name = None

    if state_code:
        products = products.filter(seller__profile__state=state_code)
        state_name = dict(Profile.STATE_CHOICES).get(state_code)

    products = list(products)
    products.sort(key=lambda p: seller_rank_score(p.seller), reverse=True)

    return render(request, "products/product_list.html", {
        "products": products,
        "categories": categories,
        "selected_state": state_name,
    })


# =========================
# 📄 PRODUCT DETAIL
# =========================
def product_detail(request, id):
    product = get_object_or_404(Product, id=id, is_active=True)

    if product.seller.profile.verification_status != "approved":
        return redirect("products:product_list")

    analytics, _ = ProductAnalytics.objects.get_or_create(product=product)
    analytics.views += 1
    analytics.save()

    ProductView.objects.create(product=product)

    return render(request, "products/product_detail.html", {
        "product": product,
        "analytics": analytics,
    })


# =========================
# ➕ ADD PRODUCT
# =========================
@login_required
def add_product(request):
    profile = request.user.profile

    if profile.role not in ["seller", "both"]:
        return redirect("core:home")

    if profile.verification_status != "approved":
        return redirect("accounts:seller_verification")

    categories = Category.objects.filter(is_active=True)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 0))
        if quantity <= 0:
            return render(request, "products/add_product.html", {
                "categories": categories,
                "error": "Quantity must be greater than 0",
            })

        category = get_object_or_404(Category, id=request.POST.get("category"))

        Product.objects.create(
            seller=request.user,
            category=category,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            price=request.POST.get("price"),
            quantity=quantity,
            location=profile.state,
            product_image=request.FILES.get("product_image"),
            is_active=True,
        )

        return redirect("products:seller_dashboard")

    return render(request, "products/add_product.html", {"categories": categories})


# =========================
# 📊 SELLER DASHBOARD
# =========================
@login_required
def seller_dashboard(request):
    profile = request.user.profile

    if profile.role not in ["seller", "both"]:
        return redirect("products:product_list")

    products = Product.objects.filter(seller=request.user)

    views_count = (
        ProductAnalytics.objects
        .filter(product__seller=request.user)
        .aggregate(total=Sum("views"))["total"]
    ) or 0

    today = timezone.now().date()
    start = today - timedelta(days=6)

    weekly_views = (
        ProductView.objects
        .filter(product__seller=request.user, created_at__date__gte=start)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
    )

    week_labels, week_data = [], []
    for i in range(7):
        d = start + timedelta(days=i)
        week_labels.append(d.strftime("%a"))
        week_data.append(next((x["count"] for x in weekly_views if x["day"] == d), 0))

    phone_clicks = (
        ProductAnalytics.objects
        .filter(product__seller=request.user)
        .aggregate(total=Sum("phone_clicks"))["total"]
    ) or 0

    leads = (
        Lead.objects
        .filter(seller=request.user)
        .select_related("product", "buyer", "order")
        .order_by("-created_at")
    )
    # =========================
# 📦 SELLER ORDERS METRICS
# =========================
    seller_orders = Order.objects.filter(seller=request.user)

    total_orders = seller_orders.count()

    new_orders = seller_orders.filter(
        status__in=["placed", "confirmed"]
    ).count()

    delivered_orders = seller_orders.filter(
        status="delivered"
    ).count()

    recent_orders = seller_orders.select_related(
        "buyer"
    ).order_by("-created_at")[:5]

    metrics = seller_response_metrics(request.user)

    return render(request, "products/seller_dashboard.html", {
        "products": products,
        "leads": leads,
        "metrics": metrics,
        "views_count": views_count,
        "phone_clicks": phone_clicks,
        "week_labels": week_labels,
        "week_data": week_data,
        "total_products": products.count(),
        "total_orders":total_orders,
        "new_orders":new_orders,
        "delivered_orders":delivered_orders,
        "recent_orders":recent_orders,
    })


# =========================
# ❌ DELETE PRODUCT
# =========================
@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id, seller=request.user)
    product.delete()
    return redirect("products:seller_dashboard")


# =========================
# 🏪 DEALER PROFILE
# =========================
# products/views.py

def dealer_profile(request, username):
    dealer = get_object_or_404(User, username=username)

    products = Product.objects.filter(seller=dealer, is_active=True)
    
    # === REVIEW LOGIC START ===
    reviews = Review.objects.filter(seller=dealer).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = reviews.count()

    # Calculate Star Distribution (The Amazon Bar Chart)
    distribution = []
    if total_reviews > 0:
        for star in range(5, 0, -1):
            count = reviews.filter(rating=star).count()
            percentage = (count / total_reviews) * 100
            distribution.append({'star': star, 'pct': percentage, 'count': count})
    else:
        # Empty bars if no reviews
        for star in range(5, 0, -1):
            distribution.append({'star': star, 'pct': 0, 'count': 0})
    # === REVIEW LOGIC END ===

    return render(request, "products/dealer_profile.html", {
        "dealer": dealer,
        "profile": dealer.profile,
        "products": products,
        "metrics": seller_response_metrics(dealer),
        "trusted": is_trusted_seller(dealer),
        
        # Pass Review Data
        "reviews": reviews,
        "avg_rating": round(avg_rating, 1),
        "total_reviews": total_reviews,
        "distribution": distribution,
    })