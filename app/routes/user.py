import os
import uuid
from datetime import timedelta
from werkzeug.utils import secure_filename

from flask import Blueprint, render_template, redirect, url_for, abort, request, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc

from app import db
from app.models.user import User
from app.models.borrow import BorrowRequest, BorrowHistory, FavoriteBook
from app.models.book import PhysicalBook
from app.models.system import Notification
from app.utils.datetime import now_local
from app.utils.helpers import get_int_setting, queue_notification
from app.forms.auth_forms import ProfileUpdateForm


user_bp = Blueprint("user", __name__)


def create_notification_once(user_id, notification_type, message):
    existing_notification = Notification.query.filter_by(
        user_id=user_id,
        type=notification_type,
        message=message,
        is_read=False
    ).first()

    if existing_notification:
        return

    queue_notification(user_id, message, notification_type)


def update_user_overdue_and_deadline_notifications():
    now = now_local()
    tomorrow = now.date() + timedelta(days=1)

    active_borrows = BorrowHistory.query.filter(
        BorrowHistory.user_id == current_user.id,
        BorrowHistory.status.in_(["Borrowed", "Overdue"])
    ).all()

    for borrow in active_borrows:
        if not borrow.return_date:
            continue

        book_title = borrow.book.title if borrow.book else "a borrowed book"
        return_date = borrow.return_date.date()

        if borrow.status == "Borrowed" and borrow.return_date < now:
            borrow.status = "Overdue"

        if borrow.status == "Overdue":
            create_notification_once(
                current_user.id,
                "danger",
                f"Your borrowed book '{book_title}' is overdue. Please return it as soon as possible."
            )

        elif return_date == now.date():
            create_notification_once(
                current_user.id,
                "warning",
                f"Your borrowed book '{book_title}' is due today."
            )

        elif return_date == tomorrow:
            create_notification_once(
                current_user.id,
                "info",
                f"Your borrowed book '{book_title}' is due tomorrow."
            )

    db.session.commit()


@user_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_librarian:
        return redirect(url_for("librarian.dashboard"))
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))
    update_user_overdue_and_deadline_notifications()
    late_fine_per_day = get_int_setting("late_fine_per_day", 1000)

    active_borrows = BorrowHistory.query.filter(
        BorrowHistory.user_id == current_user.id,
        BorrowHistory.status.in_(["Borrowed", "Overdue"])
    ).order_by(
        BorrowHistory.return_date.asc()
    ).all()

    pending_requests = BorrowRequest.query.filter_by(
        user_id=current_user.id,
        status="Pending"
    ).order_by(
        desc(BorrowRequest.request_date)
    ).all()

    approved_requests = BorrowRequest.query.filter_by(
        user_id=current_user.id,
        status="Approved"
    ).order_by(
        desc(BorrowRequest.request_date)
    ).limit(5).all()

    rejected_requests = BorrowRequest.query.filter_by(
        user_id=current_user.id,
        status="Rejected"
    ).order_by(
        desc(BorrowRequest.request_date)
    ).limit(5).all()

    history = BorrowHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        desc(BorrowHistory.borrowed_at)
    ).limit(10).all()

    favorites = FavoriteBook.query.filter_by(
        user_id=current_user.id
    ).order_by(
        desc(FavoriteBook.created_at)
    ).all()

    recommendations = PhysicalBook.query.order_by(
        desc(PhysicalBook.borrow_count)
    ).limit(4).all()

    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(
        desc(Notification.created_at)
    ).all()

    total_estimated_fine = sum(
        borrow.fine_amount(late_fine_per_day)
        for borrow in active_borrows
    )

    return render_template(
        "user/dashboard.html",
        active_borrows=active_borrows,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        rejected_requests=rejected_requests,
        history=history,
        favorites=favorites,
        recommendations=recommendations,
        notifications=notifications,
        late_fine_per_day=late_fine_per_day,
        total_estimated_fine=total_estimated_fine
    )


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    from app.utils.faculty_helpers import load_faculty_choices

    form = ProfileUpdateForm()
    load_faculty_choices(form, include_empty=True)

    if form.validate_on_submit():
        existing_user = User.query.filter(
            User.username == form.username.data,
            User.id != current_user.id
        ).first()

        if existing_user:
            flash("That username is already taken. Please choose a different one.", "warning")
            return redirect(url_for("user.profile"))

        current_user.fullname = form.fullname.data
        current_user.username = form.username.data
        from app.utils.phone import normalize_phone, is_valid_phone
        from app.services.user_creation import assign_faculty

        phone_raw = (form.phone_number.data or "").strip()
        if phone_raw:
            if not is_valid_phone(phone_raw):
                flash("Enter a valid phone number.", "danger")
                return redirect(url_for("user.profile"))
            normalized_phone = normalize_phone(phone_raw)
            phone_duplicate = User.query.filter(
                User.id != current_user.id,
                User.phone_number == normalized_phone,
            ).first()
            if phone_duplicate:
                flash("Phone number already in use.", "danger")
                return redirect(url_for("user.profile"))
            current_user.phone_number = normalized_phone
        else:
            current_user.phone_number = None

        if form.faculty_id.data:
            try:
                assign_faculty(current_user, form.faculty_id.data)
            except ValueError:
                flash("Selected faculty is invalid.", "danger")
                return redirect(url_for("user.profile"))
        current_user.group_name = form.group_name.data

        if form.avatar.data:
            avatar_file = form.avatar.data
            ext = os.path.splitext(avatar_file.filename)[1]
            safe_filename = f"{uuid.uuid4().hex}{ext}"
            upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "avatars", safe_filename)
            avatar_file.save(upload_path)
            
            # Optionally delete old avatar file here
            current_user.avatar = f"uploads/avatars/{safe_filename}"

        db.session.commit()
        flash("Your profile has been updated!", "success")
        return redirect(url_for("user.profile"))
    
    elif request.method == "GET":
        form.fullname.data = current_user.fullname
        form.username.data = current_user.username
        form.phone_number.data = current_user.phone_number
        form.faculty_id.data = current_user.faculty_id or 0
        form.group_name.data = current_user.group_name

    from app.services.ranking_service import get_user_competition_stats
    from app.models import UserBadge, QuizAttempt

    comp_stats = get_user_competition_stats(current_user.id)
    badges = (
        UserBadge.query.filter_by(user_id=current_user.id)
        .order_by(UserBadge.awarded_at.desc())
        .limit(12)
        .all()
    )

    return render_template(
        "user/profile.html",
        form=form,
        comp_stats=comp_stats,
        badges=badges,
    )


@user_bp.route("/favorites")
@login_required
def favorites():
    favorite_books = FavoriteBook.query.filter_by(
        user_id=current_user.id
    ).order_by(
        desc(FavoriteBook.created_at)
    ).all()

    return render_template(
        "user/favorites.html",
        favorites=favorite_books
    )


@user_bp.route("/notifications")
@login_required
def notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(
        desc(Notification.created_at)
    ).all()

    for notification in notifications:
        notification.is_read = True

    db.session.commit()

    notification_summary = {
        "all": len(notifications),
        "success": sum(1 for item in notifications if item.type == "success"),
        "warning": sum(1 for item in notifications if item.type == "warning"),
        "danger": sum(1 for item in notifications if item.type == "danger")
    }

    return render_template(
        "user/notifications.html",
        notifications=notifications,
        notification_summary=notification_summary
    )


@user_bp.route(
    "/api/notifications/read/<int:notif_id>",
    methods=["POST"]
)
@login_required
def mark_notification_read(notif_id):
    notification = Notification.query.filter_by(
        id=notif_id,
        user_id=current_user.id
    ).first_or_404()

    notification.is_read = True

    db.session.commit()

    return {
        "success": True
    }
