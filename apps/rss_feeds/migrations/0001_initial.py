# Generated manually for RSS Feeds app

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RSSFeedSource',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('source_type', models.CharField(choices=[('bbc_sport', 'BBC Sport Football'), ('espn_soccer', 'ESPN Soccer'), ('sky_sports', 'Sky Sports Football'), ('guardian', 'Guardian Football')], max_length=20, unique=True)),
                ('feed_url', models.URLField(max_length=500)),
                ('is_active', models.BooleanField(default=True)),
                ('last_fetched', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'RSS Feed Source',
                'verbose_name_plural': 'RSS Feed Sources',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RSSFeedItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=500)),
                ('description', models.TextField(blank=True)),
                ('content', models.TextField(blank=True)),
                ('link', models.URLField(max_length=1000)),
                ('author', models.CharField(blank=True, max_length=200)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('guid', models.CharField(max_length=500, unique=True)),
                ('published_date', models.DateTimeField()),
                ('fetched_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('is_archived', models.BooleanField(default=False)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feed_items', to='rss_feeds.rssfeedsource')),
            ],
            options={
                'verbose_name': 'RSS Feed Item',
                'verbose_name_plural': 'RSS Feed Items',
                'ordering': ['-published_date'],
            },
        ),
        migrations.CreateModel(
            name='FeedFetchLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('success', 'Success'), ('error', 'Error'), ('partial', 'Partial Success')], max_length=10)),
                ('items_fetched', models.PositiveIntegerField(default=0)),
                ('items_new', models.PositiveIntegerField(default=0)),
                ('error_message', models.TextField(blank=True)),
                ('fetch_duration', models.FloatField(blank=True, help_text='Duration in seconds', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fetch_logs', to='rss_feeds.rssfeedsource')),
            ],
            options={
                'verbose_name': 'Feed Fetch Log',
                'verbose_name_plural': 'Feed Fetch Logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='rssfeeditem',
            index=models.Index(fields=['-published_date'], name='rss_feeds_r_publish_8b8c8c_idx'),
        ),
        migrations.AddIndex(
            model_name='rssfeeditem',
            index=models.Index(fields=['source', '-published_date'], name='rss_feeds_r_source__f8c8c8_idx'),
        ),
        migrations.AddIndex(
            model_name='rssfeeditem',
            index=models.Index(fields=['is_read'], name='rss_feeds_r_is_read_8b8c8c_idx'),
        ),
        migrations.AddIndex(
            model_name='rssfeeditem',
            index=models.Index(fields=['is_archived'], name='rss_feeds_r_is_arch_8b8c8c_idx'),
        ),
    ]
