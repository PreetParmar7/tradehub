from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('create/<int:product_id>/', views.create_lead, name='create'),
    path('seller/', views.seller_leads, name='seller_leads'),
    path(
        "update-status/<int:lead_id>/<str:status>/",
        views.update_status,
        name="update_status"
    ),
    path(
        "convert/<int:lead_id>/",
        views.convert_lead_to_order,
        name="convert_lead"
    ),
]

