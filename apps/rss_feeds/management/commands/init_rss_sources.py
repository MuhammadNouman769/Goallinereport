from django.core.management.base import BaseCommand
from apps.rss_feeds.services import RSSFeedManager
from apps.rss_feeds.models import RSSFeedSource


class Command(BaseCommand):
    help = 'Initialize RSS feed sources with default configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing sources',
        )

    def handle(self, *args, **options):
        self.stdout.write('Initializing RSS feed sources...')
        
        manager = RSSFeedManager()
        
        if options['force']:
            # Delete existing sources
            RSSFeedSource.objects.all().delete()
            self.stdout.write('Deleted existing sources.')
        
        # Create default sources
        manager.initialize_sources()
        
        # Display created sources
        sources = RSSFeedSource.objects.all()
        self.stdout.write(f'Created {sources.count()} RSS feed sources:')
        
        for source in sources:
            self.stdout.write(f'  - {source.name} ({source.source_type})')
            self.stdout.write(f'    URL: {source.feed_url}')
            self.stdout.write(f'    Active: {source.is_active}')
            self.stdout.write('')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully initialized RSS feed sources!')
        )
