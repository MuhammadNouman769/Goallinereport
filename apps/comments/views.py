from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json

from .models import Comment, CommentLike
from apps.story.models import Story

@login_required
def add_comment(request):
    """Add a new comment to a story"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            story_id = data.get('story_id')
            text = data.get('text')
            parent_id = data.get('parent_id')
            
            if not all([story_id, text]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required fields'
                }, status=400)
            
            story = get_object_or_404(Story, id=story_id)
            parent = None
            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id)
            
            comment = Comment.objects.create(
                story=story,
                author=request.user,
                text=text,
                parent=parent
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Comment added successfully',
                'comment': {
                    'id': comment.id,
                    'text': comment.text,
                    'author': comment.author.username,
                    'created_at': comment.created_at.isoformat(),
                    'is_reply': comment.is_reply
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    }, status=405)

@login_required
def edit_comment(request, comment_id):
    """Edit an existing comment"""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
            
            if not text:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Text is required'
                }, status=400)
            
            comment.text = text
            comment.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Comment updated successfully',
                'comment': {
                    'id': comment.id,
                    'text': comment.text,
                    'updated_at': comment.updated_at.isoformat()
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    }, status=405)

@login_required
def delete_comment(request, comment_id):
    """Delete a comment (soft delete)"""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    
    if request.method == 'POST':
        comment.is_active = False
        comment.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Comment deleted successfully'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    }, status=405)

@login_required
def like_comment(request, comment_id):
    """Like or unlike a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        like, created = CommentLike.objects.get_or_create(
            comment=comment,
            user=request.user
        )
        
        if not created:
            # Unlike
            like.delete()
            action = 'unliked'
        else:
            action = 'liked'
        
        likes_count = comment.likes.count()
        
        return JsonResponse({
            'status': 'success',
            'action': action,
            'likes_count': likes_count
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    }, status=405)

def get_comments(request, story_id):
    """Get all comments for a specific story"""
    try:
        story = get_object_or_404(Story, id=story_id)
        comments = Comment.objects.filter(
            story=story,
            is_active=True,
            parent=None  # Only top-level comments
        ).select_related('author').prefetch_related('replies', 'likes')
        
        comments_data = []
        for comment in comments:
            comment_data = {
                'id': comment.id,
                'text': comment.text,
                'author': comment.author.username,
                'created_at': comment.created_at.isoformat(),
                'likes_count': comment.likes.count(),
                'replies_count': comment.replies_count,
                'replies': []
            }
            
            # Add replies
            for reply in comment.replies.filter(is_active=True).select_related('author'):
                reply_data = {
                    'id': reply.id,
                    'text': reply.text,
                    'author': reply.author.username,
                    'created_at': reply.created_at.isoformat(),
                    'likes_count': reply.likes.count()
                }
                comment_data['replies'].append(reply_data)
            
            comments_data.append(comment_data)
        
        return JsonResponse({
            'status': 'success',
            'comments': comments_data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
