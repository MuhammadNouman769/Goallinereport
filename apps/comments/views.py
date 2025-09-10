from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from django.utils.timezone import localtime
from .models import Comment, CommentLike
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from .models import Comment
from apps.story.models import Story   # apke story model ka import
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator


@login_required
def add_comment(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        text = request.POST.get("text")
        story_slug = request.POST.get("story_slug")
        story = get_object_or_404(Story, slug=story_slug)

        comment = Comment.objects.create(
            story=story,
            author=request.user,
            text=text
        )

        # Full name ya username
        full_name = request.user.get_full_name().strip() or request.user.username

        # Avatar check
        if hasattr(request.user, "profile") and request.user.profile.avatar:
            avatar = request.user.profile.avatar.url
        else:
            avatar = static("img/default-avatar.png")

        return JsonResponse({
            "status": "success",
            "comment": {
                "id": comment.id,
                "text": comment.text,
                "author": full_name,
                "avatar": avatar,
                "created_at": comment.created_at.strftime("%b %d, %Y %H:%M")
            }
        })

    # ✅ Hamesha return ho
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@login_required
def delete_comment(request, comment_id):
    """Delete comment"""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)

    if request.method == "POST":
        comment.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)





@login_required
@csrf_protect   # ✅ CSRF check hoga
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_text = data.get("text")

            if new_text:
                comment.text = new_text
                comment.save()

                return JsonResponse({
                    "status": "success",
                    "comment": {
                        "id": comment.id,
                        "text": comment.text,
                        "author": f"{comment.author.first_name} {comment.author.last_name}".strip() or comment.author.username,
                    }
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Text is required"
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid JSON"
            }, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=405)




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


