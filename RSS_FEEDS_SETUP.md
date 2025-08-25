# RSS Feeds Setup Guide

This guide explains how to set up and use the RSS feeds functionality in the Goal Line Report application.

## Overview

The RSS feeds app fetches football news from multiple sources:
- BBC Sport Football
- ESPN Soccer
- Sky Sports Football
- Guardian Football

## Prerequisites

1. **Redis Server**: Required for Celery background tasks
2. **Python Dependencies**: Install the required packages

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Start Redis

**macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**Windows:**
Download and install Redis from https://redis.io/download

### 3. Database Setup

Run migrations to create the RSS feeds tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Initialize RSS Sources

Create the default RSS feed sources:

```bash
python manage.py init_rss_sources
```

This will create the following sources:
- BBC Sport Football
- ESPN Soccer
- Sky Sports Football
- Guardian Football

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Celery Configuration

The Celery configuration is already set up in `core/celery.py` with:
- Automatic RSS feed fetching every 30 minutes
- Daily cleanup of old feeds
- Hourly health checks

## Usage

### 1. Start Celery Worker

In a terminal, start the Celery worker:

```bash
celery -A core worker -l info
```

### 2. Start Celery Beat (Scheduler)

In another terminal, start the Celery beat scheduler:

```bash
celery -A core beat -l info
```

### 3. Manual Feed Fetching

Fetch feeds manually:

```bash
# Fetch all feeds
python manage.py fetch_rss_feeds

# Fetch from specific source
python manage.py fetch_rss_feeds --source bbc_sport

# Fetch asynchronously using Celery
python manage.py fetch_rss_feeds --async
```

### 4. Access RSS Feeds

Visit the RSS feeds page at: `/rss/`

## Features

### RSS Feed Sources Management

- **Admin Interface**: Manage sources at `/admin/rss_feeds/rssfeedsource/`
- **Enable/Disable**: Toggle sources on/off
- **Custom URLs**: Modify feed URLs if needed
- **Fetch Logs**: View fetch history and errors

### Feed Items

- **Automatic Fetching**: Feeds are fetched every 30 minutes
- **Duplicate Prevention**: Uses GUID to prevent duplicate entries
- **Content Cleaning**: Removes HTML tags and normalizes text
- **Read/Unread Status**: Track which feeds have been read
- **Archiving**: Archive old feeds to keep the list clean

### User Interface

- **Feed List**: Browse all feeds with filtering and search
- **Feed Detail**: View full feed content
- **Mark as Read**: Mark feeds as read
- **Archive**: Archive feeds you don't want to see
- **Filtering**: Filter by source, category, and search terms

## API Endpoints

### RSS Feeds API

- **GET** `/rss/api/feeds/` - Get feeds in JSON format
- **Parameters**:
  - `source`: Filter by source type
  - `limit`: Number of feeds to return (default: 50)
  - `offset`: Pagination offset (default: 0)

### AJAX Endpoints

- **POST** `/rss/feed/{id}/mark-read/` - Mark feed as read
- **POST** `/rss/feed/{id}/archive/` - Archive feed
- **POST** `/rss/fetch/` - Trigger manual feed fetch

## Monitoring

### Health Checks

The system includes automatic health checks that run every hour:

```bash
# Manual health check
python manage.py shell
>>> from apps.rss_feeds.tasks import health_check_task
>>> result = health_check_task.delay()
>>> print(result.get())
```

### Logs

Monitor Celery logs for any issues:

```bash
# View worker logs
celery -A core worker -l info

# View beat logs
celery -A core beat -l info
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis is running: `redis-cli ping`
   - Check Redis URL in settings

2. **Feed Fetching Fails**
   - Check network connectivity
   - Verify feed URLs are accessible
   - Check logs for specific error messages

3. **Celery Worker Not Starting**
   - Ensure Redis is running
   - Check Celery configuration
   - Verify all dependencies are installed

### Debug Commands

```bash
# Test Redis connection
redis-cli ping

# Test Celery connection
python manage.py shell
>>> from core.celery import app
>>> app.control.inspect().active()

# Check RSS sources
python manage.py shell
>>> from apps.rss_feeds.models import RSSFeedSource
>>> RSSFeedSource.objects.all()
```

## Customization

### Adding New Sources

1. Add the source type to `RSSFeedSource.SOURCE_CHOICES`
2. Add the feed URL to `RSSFeedFetcher.DEFAULT_FEED_URLS`
3. Run the initialization command

### Modifying Fetch Schedule

Edit the Celery beat schedule in `core/celery.py`:

```python
beat_schedule={
    'fetch-rss-feeds-every-30-minutes': {
        'task': 'rss_feeds.fetch_all_feeds',
        'schedule': 1800.0,  # 30 minutes
    },
    # Add more scheduled tasks here
}
```

### Custom Feed Processing

Extend the `RSSFeedFetcher` class in `services.py` to add custom processing logic.

## Security Considerations

- RSS feeds are fetched from external sources
- Content is cleaned to remove potentially harmful HTML
- User authentication is required for management features
- CSRF protection is enabled for all forms

## Performance

- Database indexes are created for optimal query performance
- Pagination is implemented to handle large numbers of feeds
- Background tasks prevent blocking the web interface
- Automatic cleanup prevents database bloat
