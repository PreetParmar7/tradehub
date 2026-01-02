from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('marketplace/', views.product_list, name='product_list'),
    path('add/', views.add_product, name='add_product'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('delete/<int:id>/', views.delete_product, name='delete_product'),
    path('dealer/<str:username>/', views.dealer_profile, name='dealer_profile'),
    path('<int:id>/', views.product_detail, name='product_detail'),
]
