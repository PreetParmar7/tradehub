# messaging/urls.py
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('start/<int:product_id>/', views.start_conversation, name='start'),
    path('conversation/<int:conv_id>/', views.conversation_detail, name='conversation'),
]
