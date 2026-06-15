# Akhu Library

A Flask-based library management platform for physical books, digital books, users, faculties, borrowing workflows, notifications, reviews, and reading competitions.

## Features

- Admin, librarian, and user roles
- Login, registration, password reset, and CSRF protection
- User management by faculty and group
- Physical books, copies, NN numbers, and borrowing workflows
- Digital books, PDF reading, reading progress, and bookmarks
- Waiting lists, fines, return conditions, and notifications
- Admin and librarian dashboards, statistics, and Excel exports
- Reading competitions, question bank, results, and certificates

## Tech Stack

- Python, Flask
- Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF
- PostgreSQL
- Flask-Mail
- openpyxl, reportlab
- HTML, CSS, JavaScript

## Project Structure

```text
app/
  forms/          WTForms definitions
  models/         SQLAlchemy models
  routes/         Flask blueprints
  services/       Imports, analytics, seed data, and business logic
  static/         CSS, JavaScript, images, and uploaded files
  templates/      Jinja templates
  utils/          Helper functions
migrations/       Alembic/Flask-Migrate migrations
config.py         Application configuration
run.py            Flask application entry point
requirements.txt  Python dependencies
```

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Configure `.env`.

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DB_NAME
SECRET_KEY=your-secret-key
FLASK_ENV=development
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@example.com
```

For production, enable secure cookies:

```env
FLASK_ENV=production
SESSION_COOKIE_SECURE=true
REMEMBER_COOKIE_SECURE=true
```

4. Apply database migrations.

```bash
flask --app run db upgrade
```

5. Seed initial roles, accounts, settings, and demo data when needed.

```bash
flask --app run shell
```

Inside the shell:

```python
from app.services.seed import seed_initial_data
seed_initial_data()
```

6. Run the application.

```bash
python run.py
```

Default URL: `http://localhost:5000`.

## Notes

- Keep `.env` and `.venv` out of version control.
- Use a strong private `SECRET_KEY` in production.
- Run production deployments with a WSGI server, not the Flask development server.
- PDF reading restrictions are application-level access controls and UI deterrents, not full DRM.
