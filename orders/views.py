# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from products.models import Product
from .models import (
    Cart, CartItem,
    Order, OrderItem,
    Address
)

# =========================
# 🛒 VIEW CART
# =========================
@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "orders/cart.html", {"cart": cart})


# =========================
# ➕ ADD TO CART
# =========================
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if product.seller == request.user:
        messages.error(request, "You cannot buy your own product.")
        return redirect("products:product_detail", product.id)

    if product.quantity <= 0:
        messages.error(request, "Product is out of stock.")
        return redirect("products:product_detail", product.id)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        if cart_item.quantity + 1 > product.quantity:
            messages.error(request, "Not enough stock available.")
            return redirect("products:product_detail", product.id)
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1

    cart_item.save()
    messages.success(request, "Product added to cart.")
    return redirect("orders:view_cart")


# =========================
# ❌ REMOVE FROM CART
# =========================
@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect("orders:view_cart")


# =========================
# 🧾 CHECKOUT
# =========================
@login_required
@transaction.atomic
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    if cart.items.count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("orders:view_cart")
    lat = request.POST.get("latitude") or None
    lng = request.POST.get("longitude") or None
    if request.method == "POST":
        # 1️⃣ Create address
        address = Address.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            address_line1=request.POST.get("address_line1"),
            address_line2=request.POST.get("address_line2"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
            latitude=float(lat) if lat else None,
            longitude=float(lng) if lng else None,
        )

        order_type = request.POST.get("order_type")
        if not order_type:
            messages.error(request, "Please select payment method.")
            return redirect("orders:checkout")

        # 2️⃣ Single seller assumption
        seller = cart.items.first().product.seller

        # 3️⃣ Create order
        order = Order.objects.create(
            buyer=request.user,
            seller=seller,
            address=address,
            order_type=order_type,
            total_amount=cart.total_price,
            status="placed",
        )

        # 4️⃣ Create order items + reduce stock
        for item in cart.items.select_related("product").select_for_update():
            product = item.product
            if item.quantity > product.quantity:
                messages.error(request, "Insufficient stock.")
                return redirect("orders:view_cart")

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )

            product.quantity -= item.quantity
            product.save()

        # 5️⃣ Clear cart
        cart.items.all().delete()

        # 6️⃣ Emails
        send_mail(
            "✅ Order Placed – CommerceGrid",
            f"Thank you for your order!\nOrder ID: {order.id}",
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=True
        )

        send_mail(
            "📦 New Order Received – CommerceGrid",
            f"New order received.\nOrder ID: {order.id}",
            settings.EMAIL_HOST_USER,
            [seller.email],
            fail_silently=True
        )

        return redirect("orders:order_history")

    return render(request, "orders/checkout.html", {
        "cart": cart,
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
    })


# =========================
# 📦 PLACE ORDER
# =========================
@login_required
@transaction.atomic
def place_order(request):
    if request.method != "POST":
        return redirect("orders:checkout")

    cart = get_object_or_404(Cart, user=request.user)

    if cart.items.count() == 0:
        return redirect("orders:view_cart")

    address_id = request.POST.get("address_id")
    order_type = request.POST.get("order_type")

    if not address_id or not order_type:
        messages.error(request, "Please select address and payment method.")
        return redirect("orders:checkout")

    address = get_object_or_404(Address, id=address_id, user=request.user)

    # Assume single seller cart
    seller = cart.items.first().product.seller

    order = Order.objects.create(
        buyer=request.user,
        seller=seller,
        address=address,
        order_type=order_type,
        total_amount=cart.total_price,
        status="placed",
    )

    # 🔒 Lock products for stock safety
    for item in cart.items.select_related("product").select_for_update():
        product = item.product

        if item.quantity > product.quantity:
            raise Exception("Insufficient stock")

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity,
            price=product.price
        )

        product.quantity -= item.quantity
        product.save()

    cart.items.all().delete()

    # 📧 EMAIL BUYER
    send_mail(
        subject="✅ Order Placed – CommerceGrid",
        message=f"Thank you for your order!\nOrder ID: {order.id}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.user.email],
        fail_silently=False
    )

    # 📧 EMAIL SELLER
    send_mail(
        subject="📦 New Order Received – CommerceGrid",
        message=f"You received a new order.\nOrder ID: {order.id}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[seller.email],
        fail_silently=False
    )

    return redirect("orders:order_history")


# =========================
# 📜 ORDER HISTORY (BUYER)
# =========================
@login_required
def order_history(request):
    orders = Order.objects.filter(buyer=request.user).prefetch_related("items")
    return render(request, "orders/order_history.html", {"orders": orders})


# =========================
# 🏠 ADD ADDRESS
# =========================
@login_required
def add_address(request):
    if request.method == "POST":
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            address_line1=request.POST.get("address_line1"),
            address_line2=request.POST.get("address_line2"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
            latitude=request.POST.get("latitude"),
            longitude=request.POST.get("longitude"),
        )
        return redirect("orders:checkout")

    return render(request, "orders/add_address.html")


# =========================
# 🧑‍💼 SELLER ORDERS
# =========================
@login_required
def seller_orders(request):
    orders = Order.objects.filter(seller=request.user).prefetch_related("items", "buyer")
    return render(request, "orders/seller_orders.html", {"orders": orders})


# =========================
# 🔄 UPDATE ORDER STATUS
# =========================
@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.user != order.seller:
        return redirect("core:home")

    new_status = request.POST.get("status")

    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()

        send_mail(
            subject="📦 Order Status Updated – CommerceGrid",
            message=f"Your order #{order.id} is now {order.get_status_display()}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.buyer.email],
            fail_silently=False
        )

    return redirect("orders:seller_orders")
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    status_flow = ['placed', 'confirmed', 'shipped', 'in_transit', 'delivered']

    if order.status == "cancelled":
        completed_statuses = []
        is_cancelled = True
    else:
        is_cancelled = False
        if order.status in status_flow:
            completed_statuses = status_flow[: status_flow.index(order.status) + 1]
        else:
            completed_statuses = []

    status_steps = [
        (key, label.replace("_", " "))
        for key, label in Order.STATUS_CHOICES
        if key != "cancelled"
    ]

    return render(request, "orders/order_detail.html", {
        "order": order,
        "status_steps": status_steps,
        "completed_statuses": completed_statuses,
        "is_cancelled": is_cancelled,
    })

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_order_{order.id}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # ================= HEADER =================
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "CommerceGrid Invoice")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"Order ID: {order.id}")
    c.drawString(50, height - 95, f"Order Date: {order.created_at.strftime('%d %b %Y')}")

    # ================= SELLER =================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 130, "Seller Details")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 145, order.seller.username)
    c.drawString(50, height - 160, order.seller.email)

    # ================= BUYER =================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, height - 130, "Buyer Details")
    c.setFont("Helvetica", 10)
    c.drawString(300, height - 145, order.buyer.username)
    c.drawString(300, height - 160, order.buyer.email)

    # ================= ADDRESS =================
    addr = order.address
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 200, "Delivery Address")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 215, addr.full_name)
    c.drawString(50, height - 230, addr.address_line1)
    c.drawString(50, height - 245, f"{addr.city}, {addr.get_state_display()} - {addr.pincode}")
    c.drawString(50, height - 260, f"Phone: {addr.phone}")

    # ================= ITEMS TABLE =================
    table_data = [["Product", "Quantity", "Price", "Subtotal"]]

    for item in order.items.all():
        table_data.append([
            item.product.title,
            str(item.quantity),
            f"₹{item.price}",
            f"₹{item.price * item.quantity}"
        ])

    table = Table(table_data, colWidths=[200, 80, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, height - 450)

    # ================= TOTAL =================
    c.setFont("Helvetica-Bold", 14)
    c.drawString(350, height - 480, f"Total: ₹{order.total_amount}")

    # ================= FOOTER =================
    c.setFont("Helvetica", 9)
    c.drawString(50, 50, "Thank you for shopping with CommerceGrid!")

    c.showPage()
    c.save()

    return response
