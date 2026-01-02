from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    seller = models.ForeignKey(
        User,
        related_name='reviews_received',
        on_delete=models.CASCADE
    )
    buyer = models.ForeignKey(
        User,
        related_name='reviews_given',
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seller', 'buyer')

    def __str__(self):
        return f"{self.seller.username} - {self.rating}⭐"
