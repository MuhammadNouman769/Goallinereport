from django.urls import path
from . import views

app_name = 'subscriptions'  # Namespace for URL reversing

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/<uuid:subscriber_id>/', views.unsubscribe, name='unsubscribe'),  # Use uuid parameter
]