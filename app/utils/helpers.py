import os
import uuid

from functools import wraps

from flask import (
    abort,
    current_app,
    url_for
)

from flask_login import current_user

from flask_mail import Message

from itsdangerous import (
    URLSafeTimedSerializer
)

from werkzeug.utils import secure_filename

from app import (
    db,
    mail
)

from app.models.activity import ActivityLog

from app.models.system import Notification
from app.models.system import Settings


# =====================================================
# ROLE DECORATORS
# =====================================================

def role_required(*roles):

    def decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:

                abort(401)

            if current_user.role not in roles:

                abort(403)

            return f(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(f):

    return role_required("admin")(f)


def staff_required(f):

    return role_required(
        "admin",
        "librarian"
    )(f)


# =====================================================
# FILE HELPERS
# =====================================================

def allowed_file(
    filename: str,
    allowed: set
) -> bool:

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in allowed
    )


def save_upload(
    file_storage,
    subfolder: str,
    allowed: set
) -> str | None:

    if not file_storage:

        return None

    if not file_storage.filename:

        return None

    if not allowed_file(
        file_storage.filename,
        allowed
    ):

        return None

    ext = (
        file_storage.filename
        .rsplit(".", 1)[1]
        .lower()
    )

    unique_name = (
        f"{uuid.uuid4().hex}.{ext}"
    )

    folder = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        subfolder
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    filename = secure_filename(
        unique_name
    )

    path = os.path.join(
        folder,
        filename
    )

    file_storage.save(path)

    return (
        f"uploads/{subfolder}/{filename}"
    )


# =====================================================
# ACTIVITY LOGGING
# =====================================================

def log_activity(
    user_id,
    action: str
) -> None:

    try:

        entry = ActivityLog(

            user_id=user_id,

            action=action
        )

        db.session.add(entry)

        db.session.commit()

    except Exception:

        db.session.rollback()


# =====================================================
# NOTIFICATION SYSTEM
# =====================================================

def create_notification(

    user_id: int,

    message: str,

    notif_type: str = "info"
) -> None:

    try:

        notification = Notification(

            user_id=user_id,

            message=message,

            type=notif_type
        )

        db.session.add(notification)

        db.session.commit()

    except Exception:

        db.session.rollback()


def queue_notification(

    user_id: int,

    message: str,

    notif_type: str = "info"
):

    notification = Notification(

        user_id=user_id,

        message=message,

        type=notif_type
    )

    db.session.add(notification)

    return notification


def get_setting_value(
    key: str,
    default=None
):

    setting = Settings.query.filter_by(
        key=key
    ).first()

    if not setting:
        return default

    return setting.value


def get_int_setting(
    key: str,
    default: int
) -> int:

    value = get_setting_value(
        key,
        default
    )

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# =====================================================
# EMAIL SYSTEM
# =====================================================

def send_email(

    subject: str,

    recipients: list,

    body: str
) -> bool:

    try:

        msg = Message(

            subject=subject,

            recipients=recipients,

            body=body
        )

        mail.send(msg)

        return True

    except Exception as e:

        print("MAIL ERROR:", e)

        return False


# =====================================================
# TOKEN SYSTEM
# =====================================================

def generate_reset_token(
    email: str
) -> str:

    serializer = URLSafeTimedSerializer(

        current_app.config["SECRET_KEY"]
    )

    return serializer.dumps(

        email,

        salt="password-reset-salt"
    )


def verify_reset_token(

    token: str,

    expiration: int = 3600
):

    serializer = URLSafeTimedSerializer(

        current_app.config["SECRET_KEY"]
    )

    try:

        email = serializer.loads(

            token,

            salt="password-reset-salt",

            max_age=expiration
        )

        return email

    except Exception:

        return None


# =====================================================
# PASSWORD RESET EMAIL
# =====================================================

def send_reset_email(user):

    token = generate_reset_token(
        user.email
    )

    reset_url = url_for(

        "auth.reset_password",

        token=token,

        _external=True
    )

    body = f"""
Hello {user.fullname},

A password reset request was received for your account.

Click the link below to reset your password:

{reset_url}

This link expires in 1 hour.

If you did not request this reset,
please ignore this email.

------------------------------------
Al-Khwarizmi Smart Library
"""

    return send_email(

        subject=
        "Reset Your Password",

        recipients=[user.email],

        body=body
    )


# =====================================================
# BORROW APPROVED EMAIL
# =====================================================

def send_borrow_approved_email(

    user,

    book,

    return_date
):

    body = f"""
Hello {user.fullname},

Your borrow request has been approved.

Book:
{book.title}

Return deadline:
{return_date.strftime('%Y-%m-%d')}

Please return the book before the deadline.

------------------------------------
Al-Khwarizmi Smart Library
"""

    return send_email(

        subject=
        "Borrow Request Approved",

        recipients=[user.email],

        body=body
    )


# =====================================================
# OVERDUE EMAIL
# =====================================================

def send_overdue_email(

    user,

    book,

    return_date
):

    body = f"""
Hello {user.fullname},

Your borrowed book is overdue.

Book:
{book.title}

Return deadline:
{return_date.strftime('%Y-%m-%d')}

Please return the book as soon as possible.

------------------------------------
Al-Khwarizmi Smart Library
"""

    return send_email(

        subject=
        "Book Return Reminder",

        recipients=[user.email],

        body=body
    )


def send_library_status_email(

    user,

    subject: str,

    headline: str,

    details: list[str]
) -> bool:

    body = f"""
Hello {user.fullname},

{headline}

""" + "\n".join(details) + """

------------------------------------
Al-Khwarizmi Smart Library
"""

    return send_email(

        subject=subject,

        recipients=[user.email],

        body=body
    )
