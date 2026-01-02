from django.urls import path
from . import views

app_name = 'reviews'  # This defines the namespace

urlpatterns = [
    path('add/<int:seller_id>/', views.add_review, name='add_review'),
]