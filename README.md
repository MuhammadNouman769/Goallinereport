# Goal Line Report

A Django-based web application for tracking and analyzing goal progress with comprehensive reporting features.

## Features

- 📊 Goal tracking and analytics
- 📈 Detailed progress reports
- 🎯 Goal management system
- 📱 Responsive design with Bootstrap
- ⚡ Interactive UI with jQuery
- 🗄️ PostgreSQL database integration

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, Bootstrap 5, jQuery
- **Environment**: Python 3.8+

## Project Structure

```
goallinereport/
├── core/                   # Django project settings
├── main/                   # Main application
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/              # HTML templates
├── media/                  # User uploaded files
├── venv/                   # Virtual environment
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

## Setup Instructions

### Prerequisites

1. **Python 3.8+** installed on your system
2. **PostgreSQL** database server
3. **Git** for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd goallinereport
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb goallinereport_db
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE goallinereport_db;
   \q
   ```

5. **Configure environment variables**
   Edit the `.env` file with your database credentials:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here-change-in-production
   DB_NAME=goallinereport_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

6. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Pages

- **Home** (`/`): Dashboard with overview and quick actions
- **Reports** (`/reports/`): Generate and view various reports
- **About** (`/about/`): Information about the application

### Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Interactive UI**: Smooth animations and user feedback
- **Form Validation**: Client-side validation with jQuery
- **AJAX Support**: Ready for dynamic content loading

## Development

### Adding New Pages

1. Create a new view in `main/views.py`
2. Add URL pattern in `main/urls.py`
3. Create template in `templates/` directory
4. Update navigation in `templates/base.html`

### Styling

- Custom CSS: `static/css/style.css`
- Bootstrap 5 for responsive design
- Custom color scheme and animations

### JavaScript

- Main JS file: `static/js/main.js`
- jQuery for DOM manipulation
- AJAX utilities for API calls

## Database Configuration

The application uses PostgreSQL by default. To use a different database:

1. Update `DATABASES` in `core/settings.py`
2. Install appropriate database adapter
3. Update `requirements.txt`

## Deployment

### Production Settings

1. Set `DEBUG=False` in `.env`
2. Generate a new `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Set up static file serving
5. Configure database for production

### Environment Variables

- `DEBUG`: Enable/disable debug mode
- `SECRET_KEY`: Django secret key
- `DB_*`: Database configuration
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
