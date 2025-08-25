from django.core.management.base import BaseCommand
from apps.rss_feeds.services import RSSFeedManager
from apps.rss_feeds.models import RSSFeedSource


class Command(BaseCommand):
    help = 'Fetch RSS feeds from all active sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            help='Fetch from specific source type (bbc_sport, espn_soccer, sky_sports, guardian)',
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run fetch asynchronously using Celery',
        )

    def handle(self, *args, **options):
        manager = RSSFeedManager()
        
        if options['source']:
            # Fetch from specific source
            source_type = options['source']
            self.stdout.write(f'Fetching RSS feeds from {source_type}...')
            
            if options['async']:
                from apps.rss_feeds.tasks import fetch_specific_source_task
                task = fetch_specific_source_task.delay(source_type)
                self.stdout.write(f'Task started with ID: {task.id}')
            else:
                success, message, items_fetched, items_new = manager.fetch_specific_source(source_type)
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {message}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'✗ {message}')
                    )
        else:
            # Fetch from all sources
            self.stdout.write('Fetching RSS feeds from all active sources...')
            
            if options['async']:
                from apps.rss_feeds.tasks import fetch_all_feeds_task
                task = fetch_all_feeds_task.delay()
                self.stdout.write(f'Task started with ID: {task.id}')
            else:
                results = manager.fetch_all_feeds()
                
                total_items_fetched = 0
                total_items_new = 0
                successful_sources = 0
                
                for source_name, (success, message, items_fetched, items_new) in results.items():
                    if success:
                        successful_sources += 1
                        total_items_fetched += items_fetched
                        total_items_new += items_new
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ {source_name}: {message}')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'✗ {source_name}: {message}')
                        )
                
                self.stdout.write('')
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fetch completed. Sources: {successful_sources}/{len(results)}, '
                        f'Items fetched: {total_items_fetched}, New items: {total_items_new}'
                    )
                )
