# leads/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from products.models import Product
from orders.models import Order, OrderItem, Address
from messaging.models import Conversation, Message
from .models import Lead


# =========================
# 🧾 CREATE LEAD (BUYER)
# =========================
@login_required
def create_lead(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    seller = product.seller
    buyer = request.user

    if buyer == seller:
        return redirect("products:product_detail", product_id)

    if seller.profile.verification_status != "approved":
        return redirect("products:product_detail", product_id)

    if request.method == "POST":
        quantity = request.POST.get("quantity")
        message = request.POST.get("message")

        lead = Lead.objects.create(
            seller=seller,
            buyer=buyer,
            product=product,
            status="new"
        )

        conversation, _ = Conversation.objects.get_or_create(
            buyer=buyer,
            seller=seller,
            product=product
        )

        Message.objects.create(
            conversation=conversation,
            sender=buyer,
            content=f"Enquiry:\n{message}\n\nQuantity: {quantity}"
        )

        return redirect("messaging:conversation", conversation.id)

    return render(request, "leads/create_lead.html", {"product": product})


# =========================
# 🧑‍💼 SELLER LEADS
# =========================
@login_required
def seller_leads(request):
    profile = request.user.profile

    if profile.role not in ["seller", "both"] or profile.verification_status != "approved":
        return redirect("core:home")

    leads = (
        Lead.objects
        .filter(seller=request.user)
        .select_related("product", "buyer", "order")
        .order_by("-created_at")
    )

    return render(request, "leads/seller_leads.html", {"leads": leads})


# =========================
# 🔄 UPDATE LEAD STATUS
# =========================
@login_required
def update_status(request, lead_id, status):
    lead = get_object_or_404(Lead, id=lead_id, seller=request.user)

    allowed = ["interested", "not_interested", "call_later"]

    if status in allowed:
        lead.status = status
        lead.reminder_at = (
            timezone.now() + timezone.timedelta(days=2)
            if status == "call_later"
            else None
        )
        lead.save()

    return redirect("products:seller_dashboard")


# =========================
# 🔥 CONVERT LEAD → ORDER
# =========================
@login_required
@transaction.atomic
def convert_lead_to_order(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id, seller=request.user)

    if lead.status == "converted":
        messages.warning(request, "Lead already converted.")
        return redirect("products:seller_dashboard")

    product = lead.product

    if product.quantity <= 0:
        messages.error(request, "Product out of stock.")
        return redirect("products:seller_dashboard")

    if not lead.buyer:
        messages.error(request, "Lead has no buyer.")
        return redirect("products:seller_dashboard")

    address = Address.objects.filter(user=lead.buyer).first()
    if not address:
        messages.error(request, "Buyer has no address.")
        return redirect("products:seller_dashboard")

    # ✅ CREATE ORDER
    order = Order.objects.create(
        buyer=lead.buyer,
        seller=request.user,
        address=address,
        order_type="enquiry",
        status="confirmed",
        total_amount=product.price,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price,
    )

    product.quantity -= 1
    product.save()

    lead.order = order
    lead.status = "converted"
    lead.save()

    # 📧 EMAIL BUYER
    if lead.buyer.email:
        send_mail(
            "Your enquiry is now an order",
            f"Your enquiry for {product.title} is converted.\nOrder ID: {order.id}",
            settings.EMAIL_HOST_USER,
            [lead.buyer.email],
            fail_silently=True,
        )

    # 📧 EMAIL SELLER
    send_mail(
        "Enquiry converted to order",
        f"Order #{order.id} created from enquiry.",
        settings.EMAIL_HOST_USER,
        [request.user.email],
        fail_silently=True,
    )

    messages.success(request, "Lead converted to order.")
    return redirect("products:seller_dashboard")
