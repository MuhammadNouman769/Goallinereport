# apps/glrdesign/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('author/', views.author, name='glr_author'),
    path('blog-details/', views.glr_blog_details, name='glr_blog_details'),
    path('column-layout/', views.glr_column_layout, name='glr_column_layout'),
    path('coming-soon/', views.glr_coming_soon, name='glr_coming_soon'),
    path('error/', views.glr_error, name='glr_error'),
]
