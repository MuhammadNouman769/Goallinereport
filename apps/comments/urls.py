from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('add/', views.add_comment, name='add_comment'),
    path('edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('get/<int:story_id>/', views.get_comments, name='get_comments'),
]
