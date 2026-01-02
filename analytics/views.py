from django.shortcuts import render
from django.http import JsonResponse
from products.models import Product
from .models import ProductAnalytics

def phone_click(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    analytics, _ = ProductAnalytics.objects.get_or_create(product=product)
    analytics.phone_clicks += 1
    analytics.save()

    return JsonResponse({"status": "ok"})

# Create your views here.
def track_phone_click(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    PhoneClick.objects.create(product=product)
    return JsonResponse({"success": True})
