from django.urls import path
from . import views

app_name = 'story'

urlpatterns = [
    path('', views.story_list, name='story_list'),
    path('create/', views.story_create, name='story_create'),
    path('my-stories/', views.my_stories, name='my_stories'),
    path('<int:pk>/', views.story_detail, name='story_detail'),
    path('<int:pk>/edit/', views.story_edit, name='story_edit'),
    path('<int:pk>/delete/', views.story_delete, name='story_delete'),
    path('<int:pk>/like/', views.like_story, name='like_story'),
]
