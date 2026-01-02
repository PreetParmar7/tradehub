from django.db import models
from products.models import Product

class ProductAnalytics(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="analytics"
    )
    views = models.PositiveIntegerField(default=0)
    phone_clicks = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.title} analytics"

from django.db import models
from products.models import Product

class ProductView(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="views"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"View: {self.product.title}"

class PhoneClick(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
