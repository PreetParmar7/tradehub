from django.urls import path
from . import views

app_name = "orders"

# orders/urls.py
urlpatterns = [
    path("cart/", views.view_cart, name="view_cart"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.checkout, name="checkout"),   # 👈 NEW
    path("place-order/", views.place_order, name="place_order"),
    path("address/add/", views.add_address, name="add_address"),
    path("history/", views.order_history, name="order_history"),

    path("seller/orders/", views.seller_orders, name="seller_orders"),
    path("order/<int:order_id>/status/", views.update_order_status, name="update_status"),
    path("seller/update-status/<int:order_id>/", views.update_order_status, name="update_order_status"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("invoice/<int:order_id>/", views.download_invoice, name="download_invoice"),
    path("detail/<int:order_id>/", views.order_detail, name="order_detail"),

]   
