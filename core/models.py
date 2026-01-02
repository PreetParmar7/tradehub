from django.db import models

# Create your models here.
class Industry(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, blank=True)  # emoji fallback
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
