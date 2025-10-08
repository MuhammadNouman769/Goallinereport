from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from apps.story.models import Story
from .models import Subscriber

@receiver(post_save, sender=Story)
def notify_subscribers_on_publish(sender, instance, **kwargs):
    if instance.status == 'published' and instance.published_at:  # Trigger only when published
        subscribers = Subscriber.objects.filter(is_active=True)
        
        if not subscribers:
            print('-----------------------------New Email Gone-----------------------------')
            return

        subject = f'New Story Published: {instance.title}'
        for subscriber in subscribers:
            context = {
                'story': instance,
                'subscriber': subscriber,
                'site_url': settings.SITE_URL,
            }
            html_message = render_to_string('subscriptions/email_new_story.html', context)
            plain_message = strip_tags(html_message)
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                fail_silently=False,
            )