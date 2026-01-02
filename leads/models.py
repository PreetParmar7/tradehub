# leads/models.py
from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from orders.models import Order

class Lead(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('converted', 'Converted to Order'),
        ('not_interested', 'Not Interested'),
        ('call_later', 'Call Later'),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leads')
    buyer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sent_leads'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    order = models.OneToOneField(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    note = models.TextField(blank=True)
    reminder_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} – {self.status}"
