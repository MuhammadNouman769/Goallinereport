import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('goallinereport')

# Set a unique app name to avoid conflicts
app.conf.task_default_queue = 'goallinereport'

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery Configuration
app.conf.update(
    # Broker settings
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Beat settings (for periodic tasks)
    beat_schedule={
        'fetch-rss-feeds-every-30-minutes': {
            'task': 'apps.rss_feeds.tasks.fetch_all_feeds_task',
            'schedule': 1800.0,  # 30 minutes
        },
        'cleanup-old-feeds-daily': {
            'task': 'apps.rss_feeds.tasks.cleanup_old_feeds_task',
            'schedule': 86400.0,  # 24 hours
        },
        'health-check-every-hour': {
            'task': 'apps.rss_feeds.tasks.health_check_task',
            'schedule': 3600.0,  # 1 hour
        },
    },
    
    # Task routing
    task_routes={
        'apps.rss_feeds.*': {'queue': 'rss_feeds'},
        '*': {'queue': 'goallinereport'},
    },
    
    # Queue definitions
    task_default_queue='goallinereport',
    task_queues={
        'goallinereport': {
            'exchange': 'goallinereport',
            'routing_key': 'goallinereport',
        },
        'rss_feeds': {
            'exchange': 'rss_feeds',
            'routing_key': 'rss_feeds',
        },
    },
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_always_eager=False,  # Set to True for testing
    
    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
