# messaging/models.py
from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Conversation(models.Model):
    buyer = models.ForeignKey(User, related_name='buyer_conversations', on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='seller_conversations', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('buyer', 'seller', 'product')

    def __str__(self):
        return f"{self.buyer} ↔ {self.seller} ({self.product.title})"
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message by {self.sender}"
