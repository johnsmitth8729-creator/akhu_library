import os

from flask import Flask, session, request, current_app, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_mail import Mail

from config import Config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    if (
        app.config.get("IS_PRODUCTION")
        and app.config.get("SECRET_KEY") == "change-me-in-production-please"
    ):
        raise RuntimeError("SECRET_KEY must be set in production.")

    os.makedirs(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "covers"
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "pdfs"
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "avatars"
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "announcements"
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            os.path.dirname(app.root_path),
            "database"
        ),
        exist_ok=True
    )

    # Backups directory at project root
    os.makedirs(
        os.path.join(
            os.path.dirname(app.root_path),
            "backups"
        ),
        exist_ok=True
    )

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    login_manager.login_message = "Please sign in to continue."

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.books import books_bp
    from app.routes.user import user_bp
    from app.routes.librarian import librarian_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.competitions import competitions_bp
    from app.routes.questions import questions_bp
    from app.routes.categories import categories_bp
    from app.routes.superadmin import superadmin_bp

    app.register_blueprint(main_bp)

    app.register_blueprint(
        auth_bp,
        url_prefix="/auth"
    )

    app.register_blueprint(
        books_bp,
        url_prefix="/books"
    )

    app.register_blueprint(
        user_bp,
        url_prefix="/user"
    )

    app.register_blueprint(
        librarian_bp,
        url_prefix="/librarian"
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/admin"
    )

    app.register_blueprint(
        api_bp,
        url_prefix="/api"
    )

    app.register_blueprint(
        competitions_bp,
        url_prefix="/competitions"
    )

    app.register_blueprint(
        questions_bp,
        url_prefix="/questions"
    )

    app.register_blueprint(
        categories_bp,
        url_prefix="/categories"
    )

    app.register_blueprint(
        superadmin_bp,
        url_prefix="/superadmin"
    )

    os.makedirs(
        os.path.join(app.config["UPLOAD_FOLDER"], "certificates"),
        exist_ok=True,
    )

    # ------------------------------------------------------------------
    # Seed SuperAdmin from environment variables
    # ------------------------------------------------------------------
    with app.app_context():
        sa_email = os.environ.get("SUPERADMIN_EMAIL", "").strip()
        sa_username = os.environ.get("SUPERADMIN_USERNAME", "").strip()
        sa_password = os.environ.get("SUPERADMIN_PASSWORD", "").strip()
        sa_password_hash = os.environ.get("SUPERADMIN_PASSWORD_HASH", "").strip()

        if not sa_email:
            app.logger.warning("SuperAdmin seeding skipped: SUPERADMIN_EMAIL not set.")
        elif not sa_password_hash and not sa_password:
            app.logger.warning("SuperAdmin seeding skipped: Neither SUPERADMIN_PASSWORD_HASH nor SUPERADMIN_PASSWORD set.")
        else:
            try:
                from app.models.user import User
                from werkzeug.security import generate_password_hash

                if not sa_password_hash and sa_password:
                    sa_password_hash = generate_password_hash(sa_password, method="pbkdf2:sha256", salt_length=16)

                # Search by either email or username
                existing_user = User.query.filter(
                    (User.email == sa_email) | (User.username == sa_username)
                ).first()

                if existing_user:
                    app.logger.info(f"Existing user found matching SuperAdmin criteria (ID: {existing_user.id}, Username: {existing_user.username}). Updating to superadmin role.")
                    existing_user.role = User.ROLE_SUPERADMIN
                    existing_user.email_verified = True
                    if existing_user.email != sa_email:
                        existing_user.email = sa_email
                    if existing_user.username != sa_username:
                        existing_user.username = sa_username
                    existing_user.password_hash = sa_password_hash
                    db.session.commit()
                    app.logger.info("SuperAdmin user updated successfully.")
                else:
                    sa = User(
                        fullname="Super Administrator",
                        username=sa_username,
                        email=sa_email,
                        password_hash=sa_password_hash,
                        role=User.ROLE_SUPERADMIN,
                        email_verified=True,
                    )
                    db.session.add(sa)
                    db.session.commit()
                    app.logger.info(f"SuperAdmin user created successfully (Username: {sa_username}).")
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"SuperAdmin seeding failed: {e}")

    # ------------------------------------------------------------------
    # Emergency mode hooks
    # ------------------------------------------------------------------
    @app.before_request
    def _check_emergency_modes():
        """Block/redirect users based on emergency toggle settings."""
        # Skip static files and the superadmin routes themselves
        if request.endpoint and (
            request.endpoint.startswith("superadmin.") or
            request.endpoint.startswith("static") or
            request.endpoint in ("auth.login", "auth.logout")
        ):
            return

        try:
            from flask_login import current_user
            from app.models.system import Settings

            def _get_setting(key):
                s = Settings.query.filter_by(key=key).first()
                return s.value if s else "false"

            # Emergency lockdown – only superadmin allowed
            if _get_setting("emergency_lockdown") == "true":
                if not (current_user.is_authenticated and current_user.is_superadmin):
                    return redirect(url_for("main.emergency_lockdown"))

            # Maintenance mode – only staff allowed
            if _get_setting("maintenance_mode") == "true":
                if not (current_user.is_authenticated and current_user.is_staff):
                    return redirect(url_for("main.maintenance"))

            # Read-only mode – flash warning on mutating requests
            if _get_setting("read_only_mode") == "true":
                if request.method not in ("GET", "HEAD", "OPTIONS"):
                    if not (current_user.is_authenticated and current_user.is_superadmin):
                        flash("The platform is currently in read-only mode.", "warning")
                        return redirect(request.referrer or url_for("main.home"))
        except Exception:
            pass  # Never break requests due to settings errors

    @app.context_processor
    def inject_globals():
        from app.models.system import Notification, SiteBanner
        from app.utils.datetime import now_local

        unread_notifications = 0
        navbar_notifications = []
        active_banner = None
        is_impersonating = False

        try:
            from flask_login import current_user

            if current_user.is_authenticated:
                unread_notifications = Notification.query.filter_by(
                    user_id=current_user.id,
                    is_read=False
                ).count()

                navbar_notifications = Notification.query.filter_by(
                    user_id=current_user.id
                ).order_by(
                    Notification.created_at.desc()
                ).limit(5).all()

            is_impersonating = "impersonator_id" in session

        except AttributeError:
            # Flask-Login raises AttributeError when current_user is accessed
            # outside a fully initialised request (e.g. during static-asset
            # serving or before the request context is ready). All other
            # exceptions propagate normally so DB errors are not silenced.
            pass

        try:
            active_banner = SiteBanner.query.filter_by(enabled=True).first()
            if active_banner and not active_banner.banner_text:
                active_banner = None
        except Exception:
            pass

        return {
            "now": now_local(),
            "unread_notifications": unread_notifications,
            "navbar_notifications": navbar_notifications,
            "active_banner": active_banner,
            "is_impersonating": is_impersonating,
        }

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        flash(
            "Your session token expired or is missing. Please refresh the page and try again.",
            "warning"
        )

        return redirect(request.referrer or url_for("main.home"))

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

    return app
