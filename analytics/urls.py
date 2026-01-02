from django.urls import path
from . import views

urlpatterns = [
    path("phone-click/<int:product_id>/", views.phone_click),
]
