from django.urls import path
from . import views

app_name = 'story'

urlpatterns = [
    path('', views.column_layout_grid, name='column_layout_grid'),
    # path('editor/', views.editor_page, name='editor_page'),
    # Tag filter page
    path("tag/<slug:tag_slug>/", views.column_layout_grid, name="stories_by_tag"),
    

    path('create/', views.story_create, name='story_create'),
    path('my-stories/', views.my_stories, name='my_stories'),
    path('review/', views.review_stories, name='review_stories'),
    path('stories/preview/<uuid:story_id>/', views.story_preview, name="story_preview"),

    
    # Blog detail page
    path("blog/<slug:slug>/", views.blog_details, name="blog_details"),

    # Story actions
    path('<slug:slug>/edit/', views.story_edit, name='story_edit'),
    path('preview/<int:story_id>/', views.story_preview, name='story_preview'),
    path('<slug:slug>/delete/', views.story_delete, name='story_delete'),
    path('<slug:slug>/like/', views.like_story, name='like_story'),
    path('<slug:slug>/review/', views.review_story, name='review_story'),
    path('<slug:slug>/submit-review/', views.submit_for_review, name='submit_for_review'),

    
]