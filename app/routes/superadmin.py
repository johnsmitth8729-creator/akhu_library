"""
SuperAdmin Control Center – Blueprint
Route prefix: /superadmin
Access:       role == 'superadmin' ONLY
"""
import csv
import glob
import io
import json
import os
import shutil
import subprocess
import zipfile
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, text

from app import db
from app.models.user import User
from app.models.system import (
    AuditLog,
    ImpersonationLog,
    Notification,
    Settings,
    SiteBanner,
    Announcement,
)
from app.models.book import Book, DigitalBook, PhysicalBook, Category
from app.models.borrow import BorrowRequest, BorrowHistory
from app.models.activity import ActivityLog
from app.utils.datetime import now_local

superadmin_bp = Blueprint("superadmin", __name__, template_folder="../templates/superadmin")

# ---------------------------------------------------------------------------
# Access guard
# ---------------------------------------------------------------------------

@superadmin_bp.before_request
@login_required
def _require_superadmin():
    """All superadmin routes require the superadmin role."""
    if not current_user.is_authenticated or not current_user.is_superadmin:
        abort(403)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_setting(key, default=""):
    s = Settings.query.filter_by(key=key).first()
    return s.value if s else default


def _set_setting(key, value, description=None):
    s = Settings.query.filter_by(key=key).first()
    if s:
        s.value = value
    else:
        s = Settings(key=key, value=value, description=description or "")
        db.session.add(s)
    db.session.commit()


def _log_audit(action, details=None, module=None, before=None, after=None):
    log = AuditLog(
        admin_id=current_user.id,
        action=action,
        details=details,
        ip_address=request.remote_addr,
        module=module or "superadmin",
        before_value=before,
        after_value=after,
    )
    db.session.add(log)
    db.session.commit()


def _get_backups_dir():
    return os.path.join(os.path.dirname(current_app.root_path), "backups")


def _purge_old_backups(max_count=30):
    """Delete oldest backups when count exceeds max_count."""
    backup_dir = _get_backups_dir()
    files = sorted(glob.glob(os.path.join(backup_dir, "*.zip")), key=os.path.getmtime)
    while len(files) > max_count:
        os.remove(files.pop(0))


def _readable_size(path):
    try:
        size = os.path.getsize(path)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except Exception:
        return "—"


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@superadmin_bp.route("/")
def dashboard():
    from app.models.competition import ReadingCompetition

    total_users      = User.query.count()
    total_admins     = User.query.filter_by(role=User.ROLE_ADMIN).count()
    total_librarians = User.query.filter_by(role=User.ROLE_LIBRARIAN).count()
    total_books      = Book.query.count()
    physical_books   = PhysicalBook.query.count()
    digital_books    = DigitalBook.query.count()
    total_borrowings = BorrowHistory.query.count()
    active_borrows   = BorrowHistory.query.filter_by(status="Borrowed").count()
    pending_requests = BorrowRequest.query.filter_by(status="Pending").count()
    active_announcements = Announcement.query.filter_by(status="active").count()
    active_competitions  = ReadingCompetition.query.filter_by(status="active").count()
    total_categories = Category.query.count()

    # Today's activity
    today_start = now_local().replace(hour=0, minute=0, second=0, microsecond=0)
    failed_today = AuditLog.query.filter(
        AuditLog.action.contains("FAILED_LOGIN"),
        AuditLog.created_at >= today_start,
    ).count()
    borrows_today = BorrowHistory.query.filter(BorrowHistory.borrowed_at >= today_start).count()
    books_today   = Book.query.filter(Book.created_at >= today_start).count()

    # Upload folder size
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "")
    uploads_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(upload_folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                uploads_size += os.path.getsize(fp)
        uploads_size_str = _readable_size_bytes(uploads_size)
    except Exception:
        uploads_size_str = "—"

    # Last 30 days user registrations (for chart)
    thirty_ago = now_local() - timedelta(days=29)
    reg_data = (
        db.session.query(
            func.date(User.created_at).label("day"),
            func.count(User.id).label("cnt"),
        )
        .filter(User.created_at >= thirty_ago)
        .group_by(func.date(User.created_at))
        .all()
    )
    reg_chart = {str(r.day): r.cnt for r in reg_data}

    return render_template(
        "superadmin/dashboard.html",
        total_users=total_users,
        total_admins=total_admins,
        total_librarians=total_librarians,
        total_books=total_books,
        physical_books=physical_books,
        digital_books=digital_books,
        total_borrowings=total_borrowings,
        active_borrows=active_borrows,
        pending_requests=pending_requests,
        active_announcements=active_announcements,
        active_competitions=active_competitions,
        total_categories=total_categories,
        failed_today=failed_today,
        borrows_today=borrows_today,
        books_today=books_today,
        uploads_size_str=uploads_size_str,
        reg_chart=json.dumps(reg_chart),
    )


def _readable_size_bytes(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


# ---------------------------------------------------------------------------
# Database Backup & Restore
# ---------------------------------------------------------------------------

@superadmin_bp.route("/database")
def database():
    backup_dir = _get_backups_dir()
    backups = []
    for f in sorted(glob.glob(os.path.join(backup_dir, "*.zip")), key=os.path.getmtime, reverse=True):
        backups.append({
            "filename": os.path.basename(f),
            "size": _readable_size(f),
            "created": datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M"),
        })

    # DB info
    try:
        db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
        result = db.session.execute(text("SELECT version()")).fetchone()
        db_version = result[0] if result else "—"
        table_count = db.session.execute(
            text("SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")
        ).scalar()
        db_size = db.session.execute(
            text("SELECT pg_size_pretty(pg_database_size(current_database()))")
        ).scalar()
    except Exception:
        db_version = "—"
        table_count = "—"
        db_size = "—"
        db_url = "—"

    return render_template(
        "superadmin/database.html",
        backups=backups,
        db_version=db_version,
        table_count=table_count,
        db_size=db_size,
        db_url=db_url,
    )


@superadmin_bp.route("/database/backup", methods=["POST"])
def database_backup():
    backup_dir = _get_backups_dir()
    timestamp = now_local().strftime("%Y%m%d_%H%M%S")
    db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    dump_filename = f"backup_{timestamp}.sql"
    zip_filename = f"backup_{timestamp}.zip"
    dump_path = os.path.join(backup_dir, dump_filename)
    zip_path = os.path.join(backup_dir, zip_filename)

    try:
        # Parse DB URL for pg_dump
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        env = os.environ.copy()
        env["PGPASSWORD"] = parsed.password or ""
        cmd = [
            "pg_dump",
            "-h", parsed.hostname or "localhost",
            "-p", str(parsed.port or 5432),
            "-U", parsed.username or "postgres",
            "-d", (parsed.path or "").lstrip("/"),
            "-f", dump_path,
        ]
        result = subprocess.run(cmd, env=env, capture_output=True, timeout=300)
        if result.returncode != 0:
            flash(f"Backup failed: {result.stderr.decode()}", "danger")
            return redirect(url_for("superadmin.database"))

        # Compress to ZIP
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(dump_path, dump_filename)
        os.remove(dump_path)

        # Purge old backups
        _purge_old_backups(30)

        _log_audit("DATABASE_BACKUP", f"Created backup: {zip_filename}", "database")
        flash(f"Backup created: {zip_filename}", "success")
    except FileNotFoundError:
        flash("pg_dump not found. Please install PostgreSQL tools.", "danger")
    except Exception as e:
        flash(f"Backup error: {e}", "danger")

    return redirect(url_for("superadmin.database"))


@superadmin_bp.route("/database/download/<filename>")
def database_download(filename):
    backup_dir = _get_backups_dir()
    # Security: only allow .zip files, no path traversal
    if not filename.endswith(".zip") or "/" in filename or "\\" in filename:
        abort(400)
    path = os.path.join(backup_dir, filename)
    if not os.path.exists(path):
        abort(404)
    _log_audit("DATABASE_DOWNLOAD", f"Downloaded backup: {filename}", "database")
    return send_file(path, as_attachment=True, download_name=filename)


@superadmin_bp.route("/database/delete/<filename>", methods=["POST"])
def database_delete(filename):
    backup_dir = _get_backups_dir()
    if not filename.endswith(".zip") or "/" in filename or "\\" in filename:
        abort(400)
    path = os.path.join(backup_dir, filename)
    if os.path.exists(path):
        os.remove(path)
        _log_audit("DATABASE_DELETE_BACKUP", f"Deleted backup: {filename}", "database")
        flash(f"Backup '{filename}' deleted.", "success")
    else:
        flash("Backup not found.", "danger")
    return redirect(url_for("superadmin.database"))


@superadmin_bp.route("/database/restore/<filename>", methods=["POST"])
def database_restore(filename):
    """Two-step confirmation: user must type 'RESTORE DATABASE' in the form."""
    confirm = request.form.get("confirm_text", "").strip()
    if confirm != "RESTORE DATABASE":
        flash("Restore cancelled: You must type 'RESTORE DATABASE' to confirm.", "warning")
        return redirect(url_for("superadmin.database"))

    backup_dir = _get_backups_dir()
    if not filename.endswith(".zip") or "/" in filename or "\\" in filename:
        abort(400)
    zip_path = os.path.join(backup_dir, filename)
    if not os.path.exists(zip_path):
        flash("Backup file not found.", "danger")
        return redirect(url_for("superadmin.database"))

    try:
        # Extract SQL from ZIP
        with zipfile.ZipFile(zip_path, "r") as zf:
            sql_names = [n for n in zf.namelist() if n.endswith(".sql")]
            if not sql_names:
                flash("No SQL file found in backup ZIP.", "danger")
                return redirect(url_for("superadmin.database"))
            sql_name = sql_names[0]
            extract_dir = os.path.join(backup_dir, "_restore_tmp")
            os.makedirs(extract_dir, exist_ok=True)
            zf.extract(sql_name, extract_dir)
            sql_path = os.path.join(extract_dir, sql_name)

        db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        env = os.environ.copy()
        env["PGPASSWORD"] = parsed.password or ""
        cmd = [
            "psql",
            "-h", parsed.hostname or "localhost",
            "-p", str(parsed.port or 5432),
            "-U", parsed.username or "postgres",
            "-d", (parsed.path or "").lstrip("/"),
            "-f", sql_path,
        ]
        result = subprocess.run(cmd, env=env, capture_output=True, timeout=600)
        shutil.rmtree(extract_dir, ignore_errors=True)

        if result.returncode != 0:
            flash(f"Restore failed: {result.stderr.decode()}", "danger")
        else:
            _log_audit("DATABASE_RESTORE", f"Restored from: {filename}", "database")
            flash(f"Database restored from '{filename}' successfully.", "success")
    except Exception as e:
        flash(f"Restore error: {e}", "danger")

    return redirect(url_for("superadmin.database"))


# ---------------------------------------------------------------------------
# System Settings
# ---------------------------------------------------------------------------

SUPERADMIN_SETTINGS_KEYS = [
    "site_name", "site_description", "contact_email",
    "maintenance_mode", "emergency_lockdown", "read_only_mode",
    "disable_registrations", "disable_digital_reading",
    "disable_competitions", "disable_file_uploads", "disable_profile_editing",
    "mail_server", "mail_port", "mail_username", "mail_password",
    "telegram_bot_token", "telegram_chat_id", "session_timeout", "max_upload_mb",
]


@superadmin_bp.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # 1. Process standard settings
        for key in SUPERADMIN_SETTINGS_KEYS:
            if key not in request.form:
                continue
            value = request.form.get(key, "").strip()
            if key in ("mail_password", "telegram_bot_token") and not value:
                continue
            old = _get_setting(key, "")
            _set_setting(key, value)
            if old != value:
                _log_audit(
                    f"SETTING_CHANGED:{key}",
                    f"Setting '{key}' changed",
                    "settings",
                    before=old,
                    after=value,
                )

        # 2. Process Logo Upload
        if "logo_file" in request.files:
            file = request.files["logo_file"]
            if file and file.filename:
                ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
                if ext == "png":
                    images_dir = os.path.join(current_app.root_path, "static", "images")
                    os.makedirs(images_dir, exist_ok=True)
                    logo_path = os.path.join(images_dir, "logo.png")
                    file.save(logo_path)
                    _log_audit("LOGO_CHANGED", "University logo image was updated", "settings")
                else:
                    flash("University Logo must be a PNG image.", "danger")
                    return redirect(url_for("superadmin.settings"))

        # 3. Process Background Upload
        if "background_file" in request.files:
            file = request.files["background_file"]
            if file and file.filename:
                ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
                if ext in ("png", "jpg", "jpeg"):
                    images_dir = os.path.join(current_app.root_path, "static", "images")
                    os.makedirs(images_dir, exist_ok=True)
                    bg_path = os.path.join(images_dir, "home_jpg.png")
                    file.save(bg_path)
                    _log_audit("HOMEPAGE_BACKGROUND_CHANGED", "Homepage background image was updated", "settings")
                else:
                    flash("Homepage Background must be a PNG or JPG/JPEG image.", "danger")
                    return redirect(url_for("superadmin.settings"))

        flash("Settings saved successfully.", "success")
        return redirect(url_for("superadmin.settings"))

    current_settings = {key: _get_setting(key, "") for key in SUPERADMIN_SETTINGS_KEYS}
    return render_template("superadmin/settings.html", current_settings=current_settings)


# ---------------------------------------------------------------------------
# Emergency Controls
# ---------------------------------------------------------------------------

EMERGENCY_TOGGLES = [
    ("maintenance_mode",        "Maintenance Mode",        "warning", "fa-tools",
     "Allows only staff to access the platform. Regular users see a maintenance page."),
    ("emergency_lockdown",      "Emergency Lockdown",      "danger",  "fa-lock",
     "Allows ONLY the SuperAdmin to access the platform. Everyone else is locked out."),
    ("read_only_mode",          "Read-Only Mode",          "info",    "fa-eye",
     "Prevents all write operations. Read-only for all users except SuperAdmin."),
    ("disable_registrations",   "Disable Registrations",   "warning", "fa-user-slash",
     "Prevents new users from registering accounts."),
    ("disable_digital_reading", "Disable Digital Reading", "warning", "fa-book-open",
     "Prevents users from opening digital books (PDF reader)."),
    ("disable_competitions",    "Disable Competitions",    "info",    "fa-trophy",
     "Hides and disables the competitions module entirely."),
    ("disable_file_uploads",    "Disable File Uploads",    "warning", "fa-upload",
     "Prevents all file uploads (covers, PDFs, avatars, announcements)."),
    ("disable_profile_editing", "Disable Profile Editing", "info",    "fa-user-edit",
     "Prevents users from editing their profile information."),
]


@superadmin_bp.route("/emergency", methods=["GET", "POST"])
def emergency():
    if request.method == "POST":
        key   = request.form.get("key", "")
        value = request.form.get("value", "")
        valid_keys = [t[0] for t in EMERGENCY_TOGGLES]
        if key not in valid_keys or value not in ("true", "false"):
            flash("Invalid toggle.", "danger")
            return redirect(url_for("superadmin.emergency"))
        old = _get_setting(key, "false")
        _set_setting(key, value)
        _log_audit(
            f"EMERGENCY_TOGGLE:{key}",
            f"Emergency toggle '{key}' set to {value}",
            "emergency",
            before=old,
            after=value,
        )
        label = next((t[1] for t in EMERGENCY_TOGGLES if t[0] == key), key)
        flash(f"'{label}' set to {'ON' if value == 'true' else 'OFF'}.", "success")
        return redirect(url_for("superadmin.emergency"))

    toggle_states = {}
    for toggle in EMERGENCY_TOGGLES:
        toggle_states[toggle[0]] = _get_setting(toggle[0], "false") == "true"

    return render_template(
        "superadmin/emergency.html",
        toggles=EMERGENCY_TOGGLES,
        toggle_states=toggle_states,
    )


# ---------------------------------------------------------------------------
# Security Center
# ---------------------------------------------------------------------------

@superadmin_bp.route("/security", methods=["GET", "POST"])
def security():
    if request.method == "POST":
        action = request.form.get("action")
        ip     = request.form.get("ip", "").strip()
        if action == "block" and ip:
            blocked_raw = _get_setting("blocked_ips", "")
            blocked_ips = [x.strip() for x in blocked_raw.split(",") if x.strip()]
            if ip not in blocked_ips:
                blocked_ips.append(ip)
                _set_setting("blocked_ips", ",".join(blocked_ips))
                _log_audit("IP_BLOCKED", f"Blocked IP: {ip}", "security")
                flash(f"IP {ip} blocked.", "success")
            else:
                flash(f"IP {ip} is already blocked.", "info")
        elif action == "unblock" and ip:
            blocked_raw = _get_setting("blocked_ips", "")
            blocked_ips = [x.strip() for x in blocked_raw.split(",") if x.strip()]
            if ip in blocked_ips:
                blocked_ips.remove(ip)
                _set_setting("blocked_ips", ",".join(blocked_ips))
                _log_audit("IP_UNBLOCKED", f"Unblocked IP: {ip}", "security")
                flash(f"IP {ip} unblocked.", "success")
            else:
                flash(f"IP {ip} not found in blocked list.", "warning")
        return redirect(url_for("superadmin.security"))

    blocked_raw = _get_setting("blocked_ips", "")
    blocked_ips = [x.strip() for x in blocked_raw.split(",") if x.strip()]

    # Recent login attempts (failed logins logged in audit)
    today_start = now_local().replace(hour=0, minute=0, second=0, microsecond=0)
    failed_today = AuditLog.query.filter(
        AuditLog.action.contains("FAILED_LOGIN"),
        AuditLog.created_at >= today_start,
    ).count()

    recent_attempts = AuditLog.query.filter(
        AuditLog.action.contains("LOGIN"),
    ).order_by(AuditLog.created_at.desc()).limit(50).all()

    # Users by role count
    role_counts = {
        "superadmin": User.query.filter_by(role=User.ROLE_SUPERADMIN).count(),
        "admin":      User.query.filter_by(role=User.ROLE_ADMIN).count(),
        "librarian":  User.query.filter_by(role=User.ROLE_LIBRARIAN).count(),
        "user":       User.query.filter_by(role=User.ROLE_USER).count(),
    }

    return render_template(
        "superadmin/security.html",
        blocked_ips=blocked_ips,
        failed_today=failed_today,
        recent_attempts=recent_attempts,
        role_counts=role_counts,
    )


# ---------------------------------------------------------------------------
# Audit Log
# ---------------------------------------------------------------------------

@superadmin_bp.route("/audit")
def audit():
    page    = request.args.get("page", 1, type=int)
    search  = request.args.get("search", "")
    module  = request.args.get("module", "")
    date_from = request.args.get("date_from", "")
    date_to   = request.args.get("date_to", "")

    q = AuditLog.query

    if search:
        q = q.filter(AuditLog.action.ilike(f"%{search}%") | AuditLog.details.ilike(f"%{search}%"))
    if module:
        q = q.filter(AuditLog.module == module)
    if date_from:
        try:
            q = q.filter(AuditLog.created_at >= datetime.strptime(date_from, "%Y-%m-%d"))
        except ValueError:
            pass
    if date_to:
        try:
            q = q.filter(AuditLog.created_at <= datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1))
        except ValueError:
            pass

    logs = q.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50)
    modules = [r[0] for r in db.session.query(AuditLog.module).distinct().filter(AuditLog.module.isnot(None)).all()]

    return render_template(
        "superadmin/audit.html",
        logs=logs,
        search=search,
        module=module,
        date_from=date_from,
        date_to=date_to,
        modules=modules,
    )


@superadmin_bp.route("/audit/export")
def audit_export():
    q = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(5000).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID", "Admin ID", "Action", "Details", "Module", "IP Address", "Before", "After", "Timestamp"])
    for log in q:
        writer.writerow([
            log.id, log.admin_id, log.action, log.details,
            log.module, log.ip_address, log.before_value, log.after_value,
            log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "",
        ])
    buf.seek(0)
    return send_file(
        io.BytesIO(buf.read().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"audit_log_{now_local().strftime('%Y%m%d_%H%M%S')}.csv",
    )


# ---------------------------------------------------------------------------
# User Management + Impersonation
# ---------------------------------------------------------------------------

@superadmin_bp.route("/users")
def users():
    page   = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    role   = request.args.get("role", "")

    q = User.query
    if search:
        q = q.filter(
            User.fullname.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%") |
            User.username.ilike(f"%{search}%")
        )
    if role:
        q = q.filter_by(role=role)

    users_page = q.order_by(User.created_at.desc()).paginate(page=page, per_page=30)

    # Recent impersonation logs
    imp_logs = ImpersonationLog.query.order_by(ImpersonationLog.started_at.desc()).limit(20).all()

    return render_template(
        "superadmin/users.html",
        users_page=users_page,
        search=search,
        role=role,
        imp_logs=imp_logs,
    )


@superadmin_bp.route("/users/<int:user_id>/impersonate", methods=["POST"])
def impersonate_user(user_id):
    target = db.session.get(User, user_id)
    if not target:
        abort(404)
    if target.is_superadmin:
        flash("Cannot impersonate another SuperAdmin.", "danger")
        return redirect(url_for("superadmin.users"))

    # Record impersonation start
    imp = ImpersonationLog(
        superadmin_id=current_user.id,
        target_user_id=target.id,
        ip_address=request.remote_addr,
    )
    db.session.add(imp)
    db.session.commit()

    session["impersonator_id"] = current_user.id
    session["impersonation_log_id"] = imp.id

    _log_audit(
        "IMPERSONATION_START",
        f"Impersonating user {target.username} (ID:{target.id})",
        "users",
    )

    login_user(target)
    flash(f"You are now impersonating {target.fullname}. Click 'Exit Impersonation' to return.", "warning")
    return redirect(url_for("main.home"))


@superadmin_bp.route("/exit-impersonation")
def exit_impersonation():
    impersonator_id = session.pop("impersonator_id", None)
    imp_log_id = session.pop("impersonation_log_id", None)

    if imp_log_id:
        imp = db.session.get(ImpersonationLog, imp_log_id)
        if imp:
            imp.ended_at = now_local()
            db.session.commit()

    if impersonator_id:
        original = db.session.get(User, impersonator_id)
        if original:
            login_user(original)
            _log_audit("IMPERSONATION_END", "Ended impersonation session", "users")
            flash("Impersonation session ended. You are back as SuperAdmin.", "success")
            return redirect(url_for("superadmin.users"))

    logout_user()
    flash("Session ended.", "info")
    return redirect(url_for("auth.login"))


# ---------------------------------------------------------------------------
# File Browser (read-only-execute: view, download, delete, search)
# ---------------------------------------------------------------------------

FILE_TABS = [
    ("covers",        "Book Covers",    "fa-image"),
    ("pdfs",          "PDF Books",      "fa-file-pdf"),
    ("announcements", "Announcements",  "fa-bullhorn"),
    ("avatars",       "Avatars",        "fa-user-circle"),
    ("certificates",  "Certificates",   "fa-certificate"),
    ("backups",       "Backups",        "fa-database"),
]


def _get_tab_path(tab_name):
    """Return the absolute path for a given tab. Backups lives outside uploads."""
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "")
    if tab_name == "backups":
        return _get_backups_dir()
    return os.path.join(upload_folder, tab_name)


@superadmin_bp.route("/files")
def files():
    active_tab = request.args.get("tab", "covers")
    search     = request.args.get("search", "").lower()
    valid_tabs = [t[0] for t in FILE_TABS]
    if active_tab not in valid_tabs:
        active_tab = "covers"

    tab_path = _get_tab_path(active_tab)
    file_list = []
    try:
        for fname in os.listdir(tab_path):
            fpath = os.path.join(tab_path, fname)
            if os.path.isfile(fpath):
                if search and search not in fname.lower():
                    continue
                file_list.append({
                    "name": fname,
                    "size": _readable_size(fpath),
                    "modified": datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M"),
                    "ext": fname.rsplit(".", 1)[-1].lower() if "." in fname else "",
                })
        file_list.sort(key=lambda x: x["modified"], reverse=True)
    except Exception:
        pass

    return render_template(
        "superadmin/files.html",
        file_list=file_list,
        active_tab=active_tab,
        search=search,
        tabs=FILE_TABS,
    )


@superadmin_bp.route("/files/download")
def files_download():
    tab  = request.args.get("tab", "")
    name = request.args.get("name", "")
    valid_tabs = [t[0] for t in FILE_TABS]
    if tab not in valid_tabs or "/" in name or "\\" in name:
        abort(400)
    tab_path = _get_tab_path(tab)
    path = os.path.join(tab_path, name)
    if not os.path.exists(path):
        abort(404)
    return send_file(path, as_attachment=True, download_name=name)


@superadmin_bp.route("/files/delete", methods=["POST"])
def files_delete():
    tab  = request.form.get("tab", "")
    name = request.form.get("name", "")
    valid_tabs = [t[0] for t in FILE_TABS]
    if tab not in valid_tabs or "/" in name or "\\" in name:
        abort(400)
    tab_path = _get_tab_path(tab)
    path = os.path.join(tab_path, name)
    if os.path.exists(path):
        os.remove(path)
        _log_audit("FILE_DELETED", f"Deleted file: {tab}/{name}", "files")
        flash(f"File '{name}' deleted.", "success")
    else:
        flash("File not found.", "danger")
    return redirect(url_for("superadmin.files", tab=tab))


# ---------------------------------------------------------------------------
# Log Reader
# ---------------------------------------------------------------------------

@superadmin_bp.route("/logs")
def logs():
    log_path = os.path.join(os.path.dirname(current_app.root_path), "app.log")
    lines = []
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()[-200:]
    except FileNotFoundError:
        # Try other common locations
        for candidate in ["logs/app.log", "flask.log", "error.log"]:
            try:
                with open(os.path.join(current_app.root_path, candidate), "r", errors="replace") as f:
                    lines = f.readlines()[-200:]
                break
            except FileNotFoundError:
                continue

    return render_template("superadmin/logs.html", log_lines=lines)


# ---------------------------------------------------------------------------
# System Notifications
# ---------------------------------------------------------------------------

@superadmin_bp.route("/notifications", methods=["GET", "POST"])
def notifications():
    if request.method == "POST":
        target  = request.form.get("target", "all")  # all, admin, librarian, user, specific
        user_id = request.form.get("user_id", "")
        message = request.form.get("message", "").strip()
        ntype   = request.form.get("ntype", "info")  # info, success, warning, danger

        if not message:
            flash("Message cannot be empty.", "danger")
            return redirect(url_for("superadmin.notifications"))

        roles_map = {
            "all":       None,
            "admin":     User.ROLE_ADMIN,
            "librarian": User.ROLE_LIBRARIAN,
            "user":      User.ROLE_USER,
        }

        if target == "specific" and user_id:
            target_users = [db.session.get(User, int(user_id))]
            target_users = [u for u in target_users if u]
        elif target in roles_map:
            role_filter = roles_map[target]
            q = User.query
            if role_filter:
                q = q.filter_by(role=role_filter)
            target_users = q.all()
        else:
            target_users = []

        count = 0
        for u in target_users:
            n = Notification(user_id=u.id, message=message, type=ntype)
            db.session.add(n)
            count += 1
        db.session.commit()

        _log_audit("NOTIFICATION_SENT", f"Sent notification to {count} users (target={target})", "notifications")
        flash(f"Notification sent to {count} users.", "success")
        return redirect(url_for("superadmin.notifications"))

    all_users = User.query.order_by(User.fullname).all()
    return render_template("superadmin/notifications.html", all_users=all_users)


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

@superadmin_bp.route("/analytics")
def analytics():
    # Subqueries to count active metrics per entity to prevent PostgreSQL GroupingErrors on polymorphic models
    user_borrow_counts = (
        db.session.query(
            BorrowHistory.user_id.label("user_id"),
            func.count(BorrowHistory.id).label("cnt")
        )
        .group_by(BorrowHistory.user_id)
        .subquery()
    )

    borrow_counts = (
        db.session.query(
            BorrowHistory.book_id.label("book_id"),
            func.count(BorrowHistory.id).label("cnt")
        )
        .group_by(BorrowHistory.book_id)
        .subquery()
    )

    from app.models.book import BookRead
    digital_read_counts = (
        db.session.query(
            BookRead.book_id.label("book_id"),
            func.count(BookRead.id).label("cnt")
        )
        .group_by(BookRead.book_id)
        .subquery()
    )

    # Most active users (by borrow counts)
    active_users = (
        db.session.query(User, func.coalesce(user_borrow_counts.c.cnt, 0).label("borrow_cnt"))
        .outerjoin(user_borrow_counts, User.id == user_borrow_counts.c.user_id)
        .order_by(text("borrow_cnt DESC"))
        .limit(10)
        .all()
    )

    # Most borrowed physical books
    top_books = (
        db.session.query(PhysicalBook, func.coalesce(borrow_counts.c.cnt, 0).label("cnt"))
        .outerjoin(borrow_counts, PhysicalBook.id == borrow_counts.c.book_id)
        .order_by(text("cnt DESC"))
        .limit(10)
        .all()
    )

    # Most read digital books
    top_digital = (
        db.session.query(DigitalBook, func.coalesce(digital_read_counts.c.cnt, 0).label("cnt"))
        .outerjoin(digital_read_counts, DigitalBook.id == digital_read_counts.c.book_id)
        .order_by(text("cnt DESC"))
        .limit(10)
        .all()
    )

    # Faculty breakdown
    from app.models.faculty import Faculty
    faculty_stats = (
        db.session.query(Faculty.name, func.count(User.id).label("cnt"))
        .join(User, User.faculty_id == Faculty.id, isouter=True)
        .group_by(Faculty.name)
        .order_by(func.count(User.id).desc())
        .all()
    )

    # Borrowing trend (last 30 days)
    thirty_ago = now_local() - timedelta(days=29)
    borrow_trend = (
        db.session.query(
            func.date(BorrowHistory.borrowed_at).label("day"),
            func.count(BorrowHistory.id).label("cnt"),
        )
        .filter(BorrowHistory.borrowed_at >= thirty_ago)
        .group_by(func.date(BorrowHistory.borrowed_at))
        .all()
    )
    borrow_chart = {str(r.day): r.cnt for r in borrow_trend}

    return render_template(
        "superadmin/analytics.html",
        active_users=active_users,
        top_books=top_books,
        top_digital=top_digital,
        faculty_stats=faculty_stats,
        borrow_chart=json.dumps(borrow_chart),
    )
