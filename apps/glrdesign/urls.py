from django.urls import path
from . import views

app_name = 'glrdesign'

urlpatterns = [
    path('', views.index, name='index'),
    path('author/', views.author, name='author'),
    path('blog-details/', views.blog_details, name='blog_details'),
    path('column-layout-grid/', views.column_layout_grid, name='column_layout_grid'),
    path('coming-soon/', views.coming_soon, name='coming_soon'),
    path('error/', views.error, name='error'),
]
