from django.urls import path
from . import views

app_name = 'story'

urlpatterns = [
    path('', views.story_list, name='story_list'),
    path('create/', views.story_create, name='story_create'),
    path('my-stories/', views.my_stories, name='my_stories'),
    path('review/', views.review_stories, name='review_stories'),
    path('<slug:slug>/', views.story_detail, name='story_detail'),
    path('<slug:slug>/edit/', views.story_edit, name='story_edit'),
    path('<slug:slug>/delete/', views.story_delete, name='story_delete'),
    path('<slug:slug>/like/', views.like_story, name='like_story'),
    path('<slug:slug>/review/', views.review_story, name='review_story'),
    path('<slug:slug>/submit-review/', views.submit_for_review, name='submit_for_review'),
]
