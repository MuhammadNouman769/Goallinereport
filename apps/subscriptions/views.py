from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .forms import SubscriptionForm
from .models import Subscriber

def subscribe(request):
    """Handle subscription form submission"""
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            if not created:
                messages.warning(request, 'You are already subscribed with this email!')
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Already subscribed!'}, status=400)
                return redirect('main:home')
            if request.user.is_authenticated:
                subscriber.user = request.user
                subscriber.save()
            messages.success(request, 'Subscribed successfully!')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Subscribed successfully!'})
            return redirect('main:home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            messages.error(request, 'Invalid email address.')
            return redirect('main:home')
    else:
        return redirect('main:home')

def unsubscribe(request, subscriber_id):
    """Handle unsubscribe request"""
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    subscriber.deactivate()
    messages.success(request, 'Unsubscribed successfully!')
    return redirect('main:home')