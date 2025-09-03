# Django Template Structure for GLR Design

This document explains the Django template structure that was created from the original HTML design.

## Template Structure

```
templates/
└── glrdesign/
    ├── base.html              # Base template with common structure
    ├── index.html             # Home page template
    └── includes/              # Reusable template components
        ├── header.html        # Header section with navigation
        ├── footer.html        # Footer section
        └── scripts.html       # JavaScript files
```

## Key Features

### 1. Base Template (`base.html`)
- Contains the common HTML structure
- Loads static files with proper Django tags
- Defines content blocks for inheritance
- Includes header, footer, and scripts

### 2. Header Include (`includes/header.html`)
- Top navigation bar with social media links
- Main navigation menu with dropdowns
- Mobile-responsive sidebar menu
- Search functionality
- Newsletter subscription popup

### 3. Footer Include (`includes/footer.html`)
- Social media links
- Newsletter subscription form
- Copyright information
- Scroll-to-top button

### 4. Scripts Include (`includes/scripts.html`)
- jQuery and other JavaScript libraries
- Custom JavaScript files
- All scripts properly loaded with Django static tags

### 5. Index Template (`index.html`)
- Extends from base template
- Contains main content sections:
  - Banner slider
  - Trending news
  - Featured posts by category
  - Latest news
  - Right sidebar with featured posts and categories

## Static Files Integration

All static files are properly referenced using Django's `{% static %}` tag:
- CSS files: `{% static 'css/filename.css' %}`
- JavaScript files: `{% static 'js/filename.js' %}`
- Images: `{% static 'img/path/image.jpg' %}`

## URL Configuration

The app is configured with the following URL pattern:
- `glrdesign/` - Main app URL prefix
- `glrdesign/` - Home page (index view)

## Django App Structure

```
apps/
└── glrdesign/
    ├── __init__.py
    ├── apps.py
    ├── urls.py
    └── views.py
```

## Usage

1. **Access the template**: Visit `/glrdesign/` in your browser
2. **Extend the base template**: Use `{% extends 'glrdesign/base.html' %}`
3. **Override content blocks**: Use `{% block content %}` to add page-specific content
4. **Include components**: Use `{% include 'glrdesign/includes/header.html' %}` for reusable parts

## Benefits of This Structure

1. **DRY Principle**: No code duplication between templates
2. **Maintainability**: Easy to update common elements
3. **Consistency**: All pages share the same header/footer
4. **Django Best Practices**: Proper use of template inheritance and includes
5. **Static File Management**: Proper integration with Django's static file system

## Customization

To customize the design:
1. Modify the base template for global changes
2. Update individual includes for specific sections
3. Override content blocks in child templates
4. Add new includes for additional components
