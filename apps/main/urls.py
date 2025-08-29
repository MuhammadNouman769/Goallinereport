from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
  
    path('about/', views.about, name='about'),
    path('reports/', views.reports, name='reports'),
    path('api/example/', views.api_example, name='api_example'),
    path('stories/', views.stories, name='stories'),
    path('', views.home, name='home'),
]
