from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('select-location/', views.select_location, name='select_location'),
    path('save-location/', views.save_location, name='save_location'),

]
