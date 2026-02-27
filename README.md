# Multimedia Project Website - Django Implementation

A lightweight, server-side rendered Django application for managing, showcasing, and collaborating on multimedia projects. Built with Python classes, Jinja templating, and minimal JavaScript.

## Project Structure

```
multimedia_project/
├── multimedia_site/          # Main Django project settings
│   ├── settings.py          # Django configuration
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI application
│   └── asgi.py              # ASGI application
├── accounts/                 # User authentication & profiles
│   ├── models.py            # User Profile, Team, TeamMembership
│   ├── views.py             # Auth, profile, team management
│   ├── urls.py              # URL routes
│   ├── admin.py             # Admin configuration
│   └── signals.py           # Auto-create profiles
├── projects/                 # Project management
│   ├── models.py            # Project, Category, Collection, Comment, Like
│   ├── views.py             # CRUD operations
│   ├── urls.py              # URL routes
│   └── admin.py             # Admin configuration
├── media/                    # Media file management
│   ├── models.py            # MediaAsset, Image, Video, Audio, Document
│   ├── views.py             # Upload, browse, manage
│   ├── urls.py              # URL routes
│   └── admin.py             # Admin configuration
├── templates/               # Jinja2 HTML templates
│   ├── base.html            # Base template
│   ├── home.html            # Home page
│   ├── accounts/            # Auth templates
│   ├── projects/            # Project templates
│   └── media/               # Media templates
├── static/                  # Static files
│   ├── css/
│   │   └── style.css        # Main stylesheet
│   └── js/
├── media/                   # Uploaded media files (created at runtime)
├── db.sqlite3               # Development database
└── manage.py                # Django management CLI
```

## Models Overview

### Accounts Models
- **UserProfile**: Extended user profile with portfolio settings
- **Team**: Collaborative team management
- **TeamMembership**: Team member roles and permissions

### Projects Models
- **ProjectCategory**: Organize projects into categories
- **Project**: Core project model with multimedia content
- **ProjectCollection**: Group related projects together
- **ProjectComment**: Collaboration feedback
- **ProjectLike**: Track user favorites

### Media Models
- **MediaAsset**: Base media file model
- **ImageMedia**: Image-specific fields
- **VideoMedia**: Video codec, quality, thumbnail
- **AudioMedia**: Audio metadata
- **DocumentMedia**: Document-specific data
- **ProjectMediaAssociation**: Link media to projects with ordering
- **MediaTag**: Tag and organize media

## Features

### User Management
- User registration with email validation
- Login/logout authentication
- Profile management with avatar
- Public/private portfolio settings
- Multiple theme options

### Project Management
- Create, edit, publish, delete projects
- Project categories and tags
- Thumbnail upload
- Status tracking (draft, published, archived)
- View counting
- Like/favorite functionality

### Collaboration
- Team creation and management
- Role-based permissions (owner, editor, viewer, commenter)
- Project comments and feedback
- Team member invitation

### Media Management
- Upload multiple file types
- Organized media library
- File metadata tracking
- Media associations with projects
- Public/private accessibility

### Portfolio
- Public project showcase
- Customizable themes
- View statistics
- Featured project highlighting

### Discovery
- Browse all public projects
- Search functionality
- Category browsing
- Tag-based filtering
- Pagination

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install django==6.0.2
pip install pillow  # Image processing
pip install psycopg2-binary  # PostgreSQL (optional)
pip install python-dotenv  # Environment variables
```

### Step 3: Apply Migrations
```bash
python manage.py migrate
```

### Step 4: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 5: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000/` in your browser.

## Usage Guide

### Creating a Project
1. Login to your account
2. Navigate to Dashboard
3. Click "Create Project"
4. Fill in project details
5. Upload media files
6. Set visibility and publish

### Uploading Media
1. Go to Media Library
2. Click "Upload"
3. Select file(s)
4. Add title and description
5. Set public/private
6. Files available immediately

### Creating Teams
1. Go to Teams
2. Click "Create Team"
3. Invite members via username
4. Assign roles (owner, editor, viewer, commenter)
5. Collaborate on projects

### Managing Portfolio
1. Edit profile
2. Choose portfolio theme
3. Toggle public visibility
4. Feature best projects
5. Share portfolio link

## Key Classes & Components

### Core Views
- `accounts.views.register()` - User registration
- `accounts.views.login_view()` - Authentication
- `projects.views.dashboard()` - User dashboard
- `projects.views.project_create()` - New project
- `media.views.media_upload()` - File upload

### Model Methods
- `Project.can_edit(user)` - Permission check
- `Project.can_view(user)` - Access check
- `Project.publish()` - Publish project
- `UserProfile.get_public_projects_count()` - Stats
- `Team.is_member(user)` - Membership check

### Decorators
- `@login_required` - Require authentication
- `@require_http_methods(["GET", "POST"])` - HTTP methods

## Database Schema

### Key Relationships
```
User (Django Auth)
  ├─ OneToOne ─> UserProfile
  ├─ ForeignKey ─> Project (as creator)
  ├─ ForeignKey ─> MediaAsset (as owner)
  └─ Many ─> Teams (through TeamMembership)

Team
  ├─ ForeignKey ─> User (as owner)
  └─ Many ─> Users (through TeamMembership)

Project
  ├─ ForeignKey ─> User (creator)
  ├─ ForeignKey ─> Team (optional)
  ├─ ForeignKey ─> ProjectCategory
  └─ Many ─> MediaAsset (through ProjectMediaAssociation)

MediaAsset
  ├─ ForeignKey ─> User (owner)
  └─ Many ─> Projects (through ProjectMediaAssociation)
```

## Configuration

### settings.py
- `DEBUG = True` - Development mode
- `ALLOWED_HOSTS = ['*']` - Change for production
- `DATABASES` - SQLite default, configure PostgreSQL
- `MEDIA_URL` - User upload path
- `MAX_UPLOAD_SIZE` - 100MB default
- `ALLOWED_FILE_TYPES` - Supported formats

### Environment Variables (.env)
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL="sqlite:///db.sqlite3"
```

## Templating System

All templates use Django's Jinja2 engine:
- `base.html` - Main layout with navigation
- Template inheritance for consistent styling
- Context processors for auth/messages
- No heavy JavaScript frameworks

### Common Template Variables
- `user` - Current authenticated user
- `user.profile` - User profile
- `messages` - Django messages
- `MEDIA_URL` - Media file URLs
- `STATIC_URL` - Static file URLs

## Security Considerations

1. **CSRF Protection**: All forms use `{% csrf_token %}`
2. **SQL Injection**: ORM prevents SQL injection
3. **Authentication**: Login required decorators
4. **Permissions**: Model-level permission checks
5. **File Validation**: Extension and size checks
6. **Input Sanitization**: Django forms validation

### Production Settings
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## API & Django Admin

### Django Admin Interface
Access at `/admin/` with superuser credentials
- Manage users and profiles
- Create categories
- Moderate comments
- Monitor file uploads
- Manage teams

### No REST API
This project uses server-side rendering. For API access, add Django REST Framework:
```bash
pip install djangorestframework
```

## Performance Optimization

1. **Database Queries**
   - Use `select_related()` for ForeignKey
   - Use `prefetch_related()` for ManyToMany
   - Add database indexes

2. **Caching**
   - Cache template fragments
   - Cache expensive queries
   - Redis for session storage

3. **Static Files**
   - Minify CSS
   - Compress images
   - Use CDN for delivery

4. **Pagination**
   - Paginate large result sets
   - Default: 12 items per page
   - 9 projects per page in browse

## Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn multimedia_site.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker
Create `Dockerfile` and `docker-compose.yml` for containerization

### Using Heroku
```bash
pip install django-heroku
# Configure Procfile and requirements.txt
```

### Database Migration
```bash
python manage.py migrate --database=production
```

## Troubleshooting

### Media Files Not Uploading
- Check `MEDIA_ROOT` directory permissions
- Verify file extension in `ALLOWED_FILE_TYPES`
- Check `MAX_UPLOAD_SIZE` limit

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Database Locked
```bash
python manage.py migrate --run-syncdb
```

### Import Errors
```bash
pip install -r requirements.txt
python manage.py shell
from accounts.models import UserProfile
```

## Contributing

1. Create feature branch
2. Make changes
3. Run tests
4. Submit pull request

## License

MIT License - Open source project

## Support

For issues or questions:
1. Check documentation
2. Review Django docs
3. Check model methods
4. Debug with `python manage.py shell`

## Future Enhancements

- [ ] Email notifications
- [ ] Advanced search with filters
- [ ] Project versioning
- [ ] Batch upload
- [ ] Social sharing
- [ ] User messaging
- [ ] Advanced analytics
- [ ] Export to PDF
- [ ] API endpoints
- [ ] Mobile app
