import os
import secrets
from datetime import timedelta
from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
    session,
    send_file,
)
from flask_login import login_required, current_user
from sqlalchemy import desc, or_
from werkzeug.utils import secure_filename
from wtforms.validators import Optional

from app import db
from app.forms.book_form import PhysicalBookForm, DigitalBookForm, FileAllowed
from app.forms.librarian_forms import CategoryForm, AuthorForm, ManualUserForm, UserImportForm
from app.forms.faculty_forms import FacultyForm
from app.models.book import Book, PhysicalBook, DigitalBook, Category, Author, BookCopy
from app.models.borrow import BorrowRequest, BorrowHistory
from app.models.user import User
from app.models.faculty import Faculty
from app.models.system import Notification
from app.utils.datetime import now_local
from app.utils.helpers import get_int_setting, send_library_status_email, log_activity
from app.utils.faculty_helpers import load_faculty_choices
from app.services.digital_rights import normalize_digital_access_flags
from app.services.analytics import build_library_analytics
from app.services.user_creation import create_user_account
from app.services.user_import import (
    parse_excel_file,
    preview_to_session_dict,
    preview_from_session_dict,
    commit_import,
    build_import_report_workbook,
    default_temp_password,
)
from app.routes.books import promote_waiting_request


librarian_bp = Blueprint("librarian", __name__)

# Mapping of source keys to endpoints for back navigation
BACK_URLS = {
    "admin": "admin.manage_users",
    "librarian": "librarian.manage_users",
}


def upload_file(file_storage, folder_name):
    if not file_storage:
        return None

    if not hasattr(file_storage, "filename"):
        return None

    if not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)

    if not filename:
        return None

    upload_dir = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        folder_name
    )

    os.makedirs(upload_dir, exist_ok=True)

    name, ext = os.path.splitext(filename)
    timestamp = now_local().strftime("%Y%m%d%H%M%S%f")
    filename = f"{name}_{timestamp}{ext}"

    filepath = os.path.join(upload_dir, filename)
    file_storage.save(filepath)

    return f"uploads/{folder_name}/{filename}"


def load_book_form_choices(form):
    categories = Category.query.order_by(Category.name.asc()).all()
    authors = Author.query.order_by(Author.fullname.asc()).all()

    form.category_id.choices = [(0, "Select Category")] + [
        (category.id, category.name)
        for category in categories
    ]

    form.author_id.choices = [(0, "Select Author")] + [
        (author.id, author.fullname)
        for author in authors
    ]


def make_digital_edit_pdf_optional(form):
    form.pdf_file.validators = [
        Optional(),
        FileAllowed(["pdf"], "PDF files only.")
    ]


def resolve_author_id(form):
    new_author_name = (form.new_author.data or "").strip()

    if new_author_name:
        existing_author = Author.query.filter(
            Author.fullname.ilike(new_author_name)
        ).first()

        if existing_author:
            return existing_author.id

        author = Author(fullname=new_author_name)
        db.session.add(author)
        db.session.flush()

        return author.id

    author_id = form.author_id.data

    if author_id == 0:
        return None

    return author_id


def resolve_category_id(form):
    new_category_name = (form.new_category.data or "").strip()

    if new_category_name:
        existing_category = Category.query.filter(
            Category.name.ilike(new_category_name)
        ).first()

        if existing_category:
            return existing_category.id

        category = Category(name=new_category_name)
        db.session.add(category)
        db.session.flush()

        return category.id

    category_id = form.category_id.data

    if category_id == 0:
        return None

    return category_id


def redirect_to_borrowings(status=""):
    if status:
        return redirect(
            url_for("librarian.manage_borrowings", status=status)
        )

    return redirect(url_for("librarian.manage_borrowings"))


def redirect_to_borrowings_with_flash(status, message, category):
    flash(message, category)
    return redirect_to_borrowings(status)


@librarian_bp.before_request
@login_required
def require_librarian():
    if not current_user.is_staff:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.home"))


@librarian_bp.route("/dashboard")
def dashboard():
    now = now_local()

    overdue_borrows = BorrowHistory.query.filter(
        BorrowHistory.status == "Borrowed",
        BorrowHistory.return_date < now
    ).all()

    for borrow in overdue_borrows:
        borrow.status = "Overdue"

    if overdue_borrows:
        db.session.commit()

    stats = {
        "pending_requests": BorrowRequest.query.filter_by(status="Pending").count(),
        "borrowed": BorrowHistory.query.filter_by(status="Borrowed").count(),
        "early_return_candidates": BorrowHistory.query.filter(
            BorrowHistory.status == "Borrowed",
            BorrowHistory.return_date > now
        ).count(),
        "overdue": BorrowHistory.query.filter_by(status="Overdue").count(),
        "physical_books": PhysicalBook.query.count(),
        "digital_books": DigitalBook.query.count()
    }

    analytics = build_library_analytics()

    return render_template(
        "librarian/dashboard.html",
        stats=stats,
        overview=analytics["overview"],
        popular_physical=analytics["popular_physical"][:5],
        popular_digital=analytics["popular_digital"][:5],
        pending_requests_list=BorrowRequest.query.filter_by(status="Pending")
        .order_by(desc(BorrowRequest.request_date))
        .limit(5)
        .all(),
    )


@librarian_bp.route("/requests")
def manage_requests():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "").strip()
    q = request.args.get("q", "").strip()

    query = BorrowRequest.query

    if q:
        query = query.join(BorrowRequest.book).join(BorrowRequest.user).outerjoin(Book.author).filter(
            or_(
                Book.title.ilike(f"%{q}%"),
                Book.isbn.ilike(f"%{q}%"),
                Author.fullname.ilike(f"%{q}%"),
                User.username.ilike(f"%{q}%"),
                User.fullname.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%")
            )
        )

    if status in ["Pending", "Queued", "Approved", "Rejected"]:
        query = query.filter(BorrowRequest.status == status)

    pagination = query.order_by(
        desc(BorrowRequest.request_date)
    ).paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    return render_template(
        "librarian/requests.html",
        pagination=pagination,
        status=status,
        q=q
    )


@librarian_bp.route("/requests/<int:req_id>/approve", methods=["POST"])
def approve_request(req_id):
    borrow_request = BorrowRequest.query.get_or_404(req_id)

    if borrow_request.status not in ["Pending", "Queued"]:
        flash("This request has already been processed.", "warning")
        return redirect(url_for("librarian.manage_requests"))

    book = borrow_request.book

    if not book or book.book_type != "physical":
        borrow_request.status = "Rejected"

        db.session.add(Notification(
            user_id=borrow_request.user_id,
            type="danger",
            message="Your borrow request was rejected because this book cannot be borrowed physically."
        ))

        db.session.commit()

        flash("This request cannot be approved.", "danger")
        return redirect(url_for("librarian.manage_requests"))

    copy_id = request.form.get("copy_id")
    if not copy_id:
        flash("You must select a specific physical copy to approve.", "danger")
        return redirect(url_for("librarian.manage_requests"))

    book_copy = BookCopy.query.get(copy_id)
    if not book_copy or book_copy.book_id != book.id or book_copy.status != "available":
        flash("Selected copy is not available.", "danger")
        return redirect(url_for("librarian.manage_requests"))

    max_active_borrows = get_int_setting("max_active_borrows", 5)
    active_borrows_count = BorrowHistory.query.filter(
        BorrowHistory.user_id == borrow_request.user_id,
        BorrowHistory.status.in_(["Borrowed", "Overdue"])
    ).count()

    if active_borrows_count >= max_active_borrows:
        borrow_request.status = "Rejected"
        db.session.add(Notification(
            user_id=borrow_request.user_id,
            type="warning",
            message=(
                f"Your borrow request for '{book.title}' was rejected because you already reached the active borrow limit."
            )
        ))
        db.session.commit()
        flash("User has reached the maximum active borrow limit.", "warning")
        return redirect(url_for("librarian.manage_requests"))

    existing_active_borrow = BorrowHistory.query.filter(
        BorrowHistory.user_id == borrow_request.user_id,
        BorrowHistory.book_id == borrow_request.book_id,
        BorrowHistory.status.in_(["Borrowed", "Overdue"])
    ).first()

    if existing_active_borrow:
        borrow_request.status = "Rejected"

        db.session.add(Notification(
            user_id=borrow_request.user_id,
            type="warning",
            message=f"Your borrow request for '{book.title}' was rejected because you already have this book borrowed."
        ))

        db.session.commit()

        flash("User already has this book borrowed.", "warning")
        return redirect(url_for("librarian.manage_requests"))

    try:
        days = int(
            request.form.get(
                "days",
                get_int_setting(
                    "default_borrow_days",
                    current_app.config.get("DEFAULT_BORROW_DAYS", 14)
                )
            )
        )
    except ValueError:
        days = get_int_setting(
            "default_borrow_days",
            current_app.config.get("DEFAULT_BORROW_DAYS", 14)
        )

    days = max(1, min(days, 180))

    now = now_local()
    return_date = now + timedelta(days=days)

    borrow_request.status = "Approved"

    borrow_history = BorrowHistory(
        user_id=borrow_request.user_id,
        book_id=borrow_request.book_id,
        copy_id=book_copy.id,
        borrowed_at=now,
        return_date=return_date,
        status="Borrowed"
    )

    book_copy.status = "borrowed"
    book.available_quantity = max(0, (book.available_quantity or 1) - 1)
    book.borrow_count = (book.borrow_count or 0) + 1

    db.session.add(borrow_history)
    db.session.add(Notification(
        user_id=borrow_request.user_id,
        type="success",
        message=(
            f"Your borrow request for '{book.title}' has been approved. "
            f"Return deadline: {return_date.strftime('%d %b %Y')}."
        )
    ))

    db.session.commit()

    try:
        from app.utils.telegram import send_telegram_notification
        send_telegram_notification(
            f"✅ <b>Kitob buyurtmasi tasdiqlandi:</b>\n"
            f"Foydalanuvchi: {borrow_request.user.fullname}\n"
            f"Kitob: {book.title}\n"
            f"Qaytarish muddati: {return_date.strftime('%Y-%m-%d')}"
        )
    except Exception:
        pass

    if borrow_request.user:
        send_library_status_email(
            borrow_request.user,
            "Borrow Request Approved",
            f"Your request for '{book.title}' has been approved.",
            [
                f"Return deadline: {return_date.strftime('%d %b %Y')}.",
                f"Loan duration: {days} days."
            ]
        )

    flash("Borrow request approved successfully.", "success")
    return redirect(url_for("librarian.manage_requests"))


@librarian_bp.route("/requests/<int:req_id>/reject", methods=["POST"])
def reject_request(req_id):
    borrow_request = BorrowRequest.query.get_or_404(req_id)

    if borrow_request.status not in ["Pending", "Queued"]:
        flash("This request has already been processed.", "warning")
        return redirect(url_for("librarian.manage_requests"))

    book_title = borrow_request.book.title if borrow_request.book else "this book"

    borrow_request.status = "Rejected"

    db.session.add(Notification(
        user_id=borrow_request.user_id,
        type="danger",
        message=f"Your borrow request for '{book_title}' has been rejected."
    ))

    db.session.commit()

    try:
        from app.utils.telegram import send_telegram_notification
        send_telegram_notification(
            f"❌ <b>Kitob buyurtmasi rad etildi:</b>\n"
            f"Foydalanuvchi: {borrow_request.user.fullname}\n"
            f"Kitob: {book_title}"
        )
    except Exception:
        pass

    if borrow_request.user:
        send_library_status_email(
            borrow_request.user,
            "Borrow Request Rejected",
            f"Your request for '{book_title}' was not approved.",
            [
                "Please review your library account or contact a librarian for more details."
            ]
        )

    flash("Borrow request rejected.", "info")
    return redirect(url_for("librarian.manage_requests"))


@librarian_bp.route("/borrowings")
def manage_borrowings():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "").strip()
    q = request.args.get("q", "").strip()
    now = now_local()
    late_fine_per_day = get_int_setting("late_fine_per_day", 1000)

    overdue_borrows = BorrowHistory.query.filter(
        BorrowHistory.status == "Borrowed",
        BorrowHistory.return_date < now
    ).all()

    for borrow in overdue_borrows:
        borrow.status = "Overdue"

    if overdue_borrows:
        db.session.commit()

    query = BorrowHistory.query

    if q:
        query = query.join(BorrowHistory.book).join(BorrowHistory.user).outerjoin(Book.author).filter(
            or_(
                Book.title.ilike(f"%{q}%"),
                Book.isbn.ilike(f"%{q}%"),
                Author.fullname.ilike(f"%{q}%"),
                User.username.ilike(f"%{q}%"),
                User.fullname.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%")
            )
        )

    if status == "Early":
        query = query.filter(
            BorrowHistory.status == "Borrowed",
            BorrowHistory.return_date > now
        )
    elif status in ["Borrowed", "Overdue", "Returned"]:
        query = query.filter(BorrowHistory.status == status)

    pagination = query.order_by(
        desc(BorrowHistory.borrowed_at)
    ).paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    return render_template(
        "librarian/borrowings.html",
        pagination=pagination,
        status=status,
        late_fine_per_day=late_fine_per_day,
        q=q
    )


@librarian_bp.route("/borrowings/<int:borrow_id>/return", methods=["POST"])
def borrowing_return(borrow_id):
    borrow = BorrowHistory.query.get_or_404(borrow_id)
    current_filter = request.form.get("status", "").strip()

    if borrow.status == "Returned":
        flash("This book has already been returned.", "warning")
        return redirect_to_borrowings(current_filter)

    if borrow.status not in ["Borrowed", "Overdue"]:
        flash("Only borrowed or overdue books can be returned.", "warning")
        return redirect_to_borrowings(current_filter)

    now = now_local()
    was_overdue = borrow.return_date < now
    late_fine_per_day = get_int_setting("late_fine_per_day", 1000)
    return_condition = request.form.get("return_condition", "good").strip().lower()
    condition_notes = request.form.get("condition_notes", "").strip() or None

    try:
        additional_charge = int(request.form.get("additional_charge", 0))
    except (TypeError, ValueError):
        additional_charge = 0

    additional_charge = max(additional_charge, 0)
    overdue_fine = borrow.fine_amount(late_fine_per_day, reference_time=now)
    final_fine_amount = overdue_fine + additional_charge

    if return_condition not in ["good", "damaged", "lost"]:
        return_condition = "good"

    borrow.status = "Returned"
    borrow.returned_at = now
    borrow.return_condition = return_condition
    borrow.condition_notes = condition_notes
    borrow.final_fine_amount = final_fine_amount
    borrow.fine_status = "unpaid" if final_fine_amount > 0 else "none"

    if borrow.book:
        if borrow.copy:
            if return_condition == "lost":
                borrow.copy.status = "lost"
            elif return_condition == "damaged":
                borrow.copy.status = "damaged"
            else:
                borrow.copy.status = "available"
        
        if return_condition == "lost":
            borrow.book.quantity = max((borrow.book.quantity or 1) - 1, 0)
            borrow.book.available_quantity = min(
                borrow.book.available_quantity or 0,
                borrow.book.quantity or 0
            )
        else:
            borrow.book.available_quantity = min(
                (borrow.book.available_quantity or 0) + 1,
                borrow.book.quantity or 1
            )

        if borrow.book.book_type == "physical":
            borrow.book.borrow_count = max((borrow.book.borrow_count or 0), 0)

        if return_condition == "lost":
            notification_type = "danger"
            message = (
                f"'{borrow.book.title}' was marked as lost during return processing. "
                f"Total charge: {final_fine_amount:,} UZS."
            )
        elif return_condition == "damaged":
            notification_type = "warning"
            message = (
                f"'{borrow.book.title}' was returned with damage notes. "
                f"Total charge: {final_fine_amount:,} UZS."
            )
        elif was_overdue:
            notification_type = "warning"
            message = (
                f"You returned '{borrow.book.title}' after the deadline. "
                f"Returned at: {now.strftime('%d %b %Y %H:%M')}. "
                f"Late fine: {final_fine_amount:,} UZS."
            )
        elif borrow.return_date > now:
            notification_type = "success"
            message = (
                f"Your early return for '{borrow.book.title}' has been confirmed. "
                f"Returned at: {now.strftime('%d %b %Y %H:%M')}."
            )
        else:
            notification_type = "success"
            message = (
                f"You successfully returned '{borrow.book.title}'. "
                f"Returned at: {now.strftime('%d %b %Y %H:%M')}."
            )

        db.session.add(Notification(
            user_id=borrow.user_id,
            type=notification_type,
            message=message
        ))

    db.session.commit()

    try:
        from app.utils.telegram import send_telegram_notification
        send_telegram_notification(
            f"📥 <b>Kitob qaytarildi:</b>\n"
            f"Foydalanuvchi: {borrow.user.fullname}\n"
            f"Kitob: {borrow.book.title}\n"
            f"Holati: {return_condition.upper()}\n"
            f"Tafsilot: {message}"
        )
    except Exception:
        pass

    if borrow.user and borrow.book:
        send_library_status_email(
            borrow.user,
            "Book Return Confirmed",
            f"Return processed for '{borrow.book.title}'.",
            [message]
        )

    if borrow.book and borrow.book.available_quantity > 0:
        promote_waiting_request(borrow.book.id)
        db.session.commit()

    flash("Book returned successfully.", "success")
    return redirect_to_borrowings(current_filter)


@librarian_bp.route("/borrowings/<int:borrow_id>/fine", methods=["POST"])
def update_borrowing_fine_status(borrow_id):
    borrow = BorrowHistory.query.get_or_404(borrow_id)
    current_filter = request.form.get("status", "").strip()
    fine_status = request.form.get("fine_status", "").strip().lower()

    if borrow.status != "Returned":
        return redirect_to_borrowings_with_flash(
            current_filter,
            "Only returned records can be settled.",
            "warning"
        )

    if fine_status not in ["paid", "waived"]:
        return redirect_to_borrowings_with_flash(
            current_filter,
            "Invalid fine status selected.",
            "danger"
        )

    if (borrow.final_fine_amount or 0) <= 0:
        return redirect_to_borrowings_with_flash(
            current_filter,
            "This record has no outstanding fine.",
            "info"
        )

    borrow.fine_status = fine_status
    db.session.commit()

    if borrow.user and borrow.book:
        if fine_status == "paid":
            notification_type = "success"
            message = (
                f"Fine for '{borrow.book.title}' has been marked as paid. "
                f"Amount: {borrow.final_fine_amount:,} UZS."
            )
        else:
            notification_type = "info"
            message = (
                f"Fine for '{borrow.book.title}' has been waived by library staff. "
                f"Amount: {borrow.final_fine_amount:,} UZS."
            )

        db.session.add(Notification(
            user_id=borrow.user_id,
            type=notification_type,
            message=message
        ))
        db.session.commit()

        send_library_status_email(
            borrow.user,
            "Fine Status Updated",
            f"The fine status for '{borrow.book.title}' has changed.",
            [message]
        )

    flash("Fine status updated successfully.", "success")
    return redirect_to_borrowings(current_filter)


@librarian_bp.route("/books")
def manage_books():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    book_type = request.args.get("type", "").strip()
    category_id = request.args.get("category_id", type=int)
    status = request.args.get("status", "").strip()

    from sqlalchemy.orm import aliased
    physical_book_alias = aliased(PhysicalBook, flat=True)

    query = Book.query.outerjoin(physical_book_alias).outerjoin(Book.author)

    if q:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{q}%"),
                Book.isbn.ilike(f"%{q}%"),
                Author.fullname.ilike(f"%{q}%")
            )
        )

    if book_type in ["physical", "digital"]:
        query = query.filter(Book.book_type == book_type)

    if category_id:
        query = query.filter(Book.category_id == category_id)

    if status:
        if status == "available":
            query = query.filter(
                or_(
                    Book.book_type == "digital",
                    physical_book_alias.available_quantity > 0
                )
            )
        elif status == "low_stock":
            query = query.filter(
                Book.book_type == "physical",
                physical_book_alias.available_quantity > 0,
                physical_book_alias.available_quantity <= physical_book_alias.quantity * 0.15
            )
        elif status == "out_of_stock":
            query = query.filter(
                Book.book_type == "physical",
                physical_book_alias.available_quantity == 0
            )
        elif status == "active":
            query = query.filter(Book.book_type == "digital")

    # Compute summary stats counts
    total_books = Book.query.count()
    physical_books = Book.query.filter(Book.book_type == "physical").count()
    digital_books = Book.query.filter(Book.book_type == "digital").count()
    total_categories = Category.query.count()

    stats = {
        "total_books": total_books,
        "physical_books": physical_books,
        "digital_books": digital_books,
        "categories": total_categories
    }

    # Fetch categories for server-side select options
    categories = Category.query.order_by(Category.name).all()

    pagination = query.order_by(
        desc(Book.created_at),
        desc(Book.id)
    ).paginate(
        page=page,
        per_page=8,
        error_out=False
    )

    return render_template(
        "librarian/books.html",
        pagination=pagination,
        q=q,
        book_type=book_type,
        category_id=category_id,
        status=status,
        stats=stats,
        categories=categories
    )


@librarian_bp.route("/books/physical/add", methods=["GET", "POST"])
def add_physical_book():
    form = PhysicalBookForm()
    load_book_form_choices(form)

    if form.validate_on_submit():
        author_id = resolve_author_id(form)
        category_id = resolve_category_id(form)

        nn_numbers_str = (form.nn_numbers.data or "").strip()
        nn_list = [n.strip() for n in nn_numbers_str.split("\n") if n.strip()]
        
        if not nn_list:
            flash("You must provide at least one NN Number.", "danger")
            return render_template("librarian/physical_book_form.html", form=form, book=None)

        if len(nn_list) != len(set(nn_list)):
            flash("Duplicate NN Numbers entered in the list.", "danger")
            return render_template("librarian/physical_book_form.html", form=form, book=None)

        existing_copies = BookCopy.query.filter(BookCopy.nn_number.in_(nn_list)).all()
        if existing_copies:
            duplicates = ", ".join([c.nn_number for c in existing_copies])
            flash(f"The following NN Numbers already exist in the system: {duplicates}", "danger")
            return render_template("librarian/physical_book_form.html", form=form, book=None)

        book = PhysicalBook(
            book_type="physical",
            title=form.title.data.strip(),
            description=form.description.data,
            isbn=(form.isbn.data or "").strip() or None,
            language=(form.language.data or "").strip() or None,
            published_year=form.published_year.data,
            author_id=author_id,
            category_id=category_id,
            quantity=len(nn_list),
            available_quantity=len(nn_list),
            library_location=(form.library_location.data or "").strip() or None,
            shelf_code=(form.shelf_code.data or "").strip() or None
        )

        cover_path = upload_file(form.cover_image.data, "covers")

        if cover_path:
            book.cover_image = cover_path

        db.session.add(book)
        db.session.flush()

        for nn in nn_list:
            copy = BookCopy(book_id=book.id, nn_number=nn, status="available")
            db.session.add(copy)

        db.session.commit()

        flash("Physical book added successfully.", "success")
        return redirect(url_for("librarian.manage_books"))

    return render_template(
        "librarian/physical_book_form.html",
        form=form,
        book=None
    )


@librarian_bp.route("/books/digital/add", methods=["GET", "POST"])
def add_digital_book():
    form = DigitalBookForm()
    load_book_form_choices(form)

    if form.validate_on_submit():
        author_id = resolve_author_id(form)
        category_id = resolve_category_id(form)
        pdf_path = upload_file(form.pdf_file.data, "pdfs")

        if not pdf_path:
            flash("Please upload a valid PDF file.", "danger")

            return render_template(
                "librarian/digital_book_form.html",
                form=form,
                book=None
            )

        allow_download, online_read_only = normalize_digital_access_flags(
            form.allow_download.data,
            form.online_read_only.data,
        )

        book = DigitalBook(
            book_type="digital",
            title=form.title.data.strip(),
            description=form.description.data,
            isbn=(form.isbn.data or "").strip() or None,
            language=(form.language.data or "").strip() or None,
            published_year=form.published_year.data,
            author_id=author_id,
            category_id=category_id,
            pdf_file=pdf_path,
            allow_download=allow_download,
            online_read_only=online_read_only,
        )

        cover_path = upload_file(form.cover_image.data, "covers")

        if cover_path:
            book.cover_image = cover_path

        db.session.add(book)
        db.session.commit()

        flash("Digital book uploaded successfully.", "success")
        return redirect(url_for("librarian.manage_books"))

    return render_template(
        "librarian/digital_book_form.html",
        form=form,
        book=None
    )


@librarian_bp.route("/books/physical/<int:book_id>/edit", methods=["GET", "POST"])
def edit_physical_book(book_id):
    book = PhysicalBook.query.get_or_404(book_id)
    form = PhysicalBookForm(obj=book)

    load_book_form_choices(form)

    if request.method == "GET":
        form.category_id.data = book.category_id or 0
        form.author_id.data = book.author_id or 0
        form.nn_numbers.data = "\n".join([c.nn_number for c in book.copies])

    if form.validate_on_submit():
        author_id = resolve_author_id(form)
        category_id = resolve_category_id(form)

        nn_numbers_str = (form.nn_numbers.data or "").strip()
        nn_list = [n.strip() for n in nn_numbers_str.split("\n") if n.strip()]
        
        if not nn_list:
            flash("You must provide at least one NN Number.", "danger")
            return render_template("librarian/physical_book_form.html", form=form, book=book)

        if len(nn_list) != len(set(nn_list)):
            flash("Duplicate NN Numbers entered in the list.", "danger")
            return render_template("librarian/physical_book_form.html", form=form, book=book)

        existing_copies = BookCopy.query.filter(
            BookCopy.nn_number.in_(nn_list),
            BookCopy.book_id != book.id
        ).all()
        if existing_copies:
            duplicates = ", ".join([c.nn_number for c in existing_copies])
            flash(f"The following NN Numbers already exist in the system for other books: {duplicates}", "danger")
            return render_template("librarian/physical_book_form.html", form=form, book=book)

        current_copies = {c.nn_number: c for c in book.copies}
        
        # Remove deleted copies
        for nn, c in current_copies.items():
            if nn not in nn_list:
                if c.status == "borrowed":
                    flash(f"Cannot remove NN Number {nn} because it is currently borrowed.", "danger")
                    return render_template("librarian/physical_book_form.html", form=form, book=book)
                db.session.delete(c)
        
        # Add new copies
        for nn in nn_list:
            if nn not in current_copies:
                new_copy = BookCopy(book_id=book.id, nn_number=nn, status="available")
                db.session.add(new_copy)
                
        db.session.flush()

        book.quantity = BookCopy.query.filter_by(book_id=book.id).count()
        book.available_quantity = BookCopy.query.filter_by(book_id=book.id, status="available").count()

        book.title = form.title.data.strip()
        book.description = form.description.data
        book.isbn = (form.isbn.data or "").strip() or None
        book.language = (form.language.data or "").strip() or None
        book.published_year = form.published_year.data
        book.author_id = author_id
        book.category_id = category_id
        book.library_location = (form.library_location.data or "").strip() or None
        book.shelf_code = (form.shelf_code.data or "").strip() or None

        cover_path = upload_file(form.cover_image.data, "covers")

        if cover_path:
            book.cover_image = cover_path

        db.session.commit()

        flash("Physical book updated successfully.", "success")
        return redirect(url_for("librarian.manage_books"))

    return render_template(
        "librarian/physical_book_form.html",
        form=form,
        book=book
    )


@librarian_bp.route("/books/digital/<int:book_id>/edit", methods=["GET", "POST"])
def edit_digital_book(book_id):
    book = DigitalBook.query.get_or_404(book_id)
    form = DigitalBookForm(obj=book)

    make_digital_edit_pdf_optional(form)
    load_book_form_choices(form)

    if request.method == "GET":
        form.category_id.data = book.category_id or 0
        form.author_id.data = book.author_id or 0

    if form.validate_on_submit():
        author_id = resolve_author_id(form)
        category_id = resolve_category_id(form)

        book.title = form.title.data.strip()
        book.description = form.description.data
        book.isbn = (form.isbn.data or "").strip() or None
        book.language = (form.language.data or "").strip() or None
        book.published_year = form.published_year.data
        book.author_id = author_id
        book.category_id = category_id
        allow_download, online_read_only = normalize_digital_access_flags(
            form.allow_download.data,
            form.online_read_only.data,
        )
        book.allow_download = allow_download
        book.online_read_only = online_read_only

        pdf_path = upload_file(form.pdf_file.data, "pdfs")

        if pdf_path:
            book.pdf_file = pdf_path

        cover_path = upload_file(form.cover_image.data, "covers")

        if cover_path:
            book.cover_image = cover_path

        db.session.commit()

        flash("Digital book updated successfully.", "success")
        return redirect(url_for("librarian.manage_books"))

    return render_template(
        "librarian/digital_book_form.html",
        form=form,
        book=book
    )


@librarian_bp.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    active_borrows = BorrowHistory.query.filter(
        BorrowHistory.book_id == book.id,
        BorrowHistory.status.in_(["Borrowed", "Overdue"])
    ).count()

    pending_requests = BorrowRequest.query.filter(
        BorrowRequest.book_id == book.id,
        BorrowRequest.status == "Pending"
    ).count()

    if active_borrows:
        flash("Cannot delete this book while it has active borrow records.", "danger")
        return redirect(url_for("librarian.manage_books"))

    if pending_requests:
        flash("Cannot delete this book while it has pending borrow requests.", "danger")
        return redirect(url_for("librarian.manage_books"))

    db.session.delete(book)
    db.session.commit()

    flash("Book deleted successfully.", "success")
    return redirect(url_for("librarian.manage_books"))


@librarian_bp.route("/categories", methods=["GET", "POST"])
def manage_categories():
    form = CategoryForm()
    q = request.args.get("q", "").strip()

    if form.validate_on_submit():
        category_name = form.name.data.strip()

        existing_category = Category.query.filter(
            Category.name.ilike(category_name)
        ).first()

        if existing_category:
            flash("Category already exists.", "warning")
        else:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()
            flash("Category added successfully.", "success")

        return redirect(url_for("librarian.manage_categories", q=q))

    categories_query = Category.query
    if q:
        categories_query = categories_query.filter(
            Category.name.ilike(f"%{q}%")
        )

    categories = categories_query.order_by(Category.name.asc()).all()

    return render_template(
        "librarian/categories.html",
        categories=categories,
        form=form,
        q=q
    )


@librarian_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
def category_delete(category_id):
    q = request.args.get("q", "").strip()
    category = Category.query.get_or_404(category_id)

    books_count = Book.query.filter_by(category_id=category.id).count()

    if books_count:
        flash("Cannot delete category with associated books.", "danger")
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted successfully.", "success")

    return redirect(url_for("librarian.manage_categories", q=q))


@librarian_bp.route("/authors", methods=["GET", "POST"])
def manage_authors():
    form = AuthorForm()
    q = request.args.get("q", "").strip()

    if form.validate_on_submit():
        author_name = form.fullname.data.strip()

        existing_author = Author.query.filter(
            Author.fullname.ilike(author_name)
        ).first()

        if existing_author:
            flash("Author already exists.", "warning")
        else:
            author = Author(fullname=author_name)
            db.session.add(author)
            db.session.commit()
            flash("Author added successfully.", "success")

        return redirect(url_for("librarian.manage_authors", q=q))

    authors_query = Author.query
    if q:
        authors_query = authors_query.filter(
            Author.fullname.ilike(f"%{q}%")
        )

    authors = authors_query.order_by(Author.fullname.asc()).all()

    return render_template(
        "librarian/authors.html",
        authors=authors,
        form=form,
        q=q
    )


@librarian_bp.route("/authors/<int:author_id>/delete", methods=["POST"])
def author_delete(author_id):
    q = request.args.get("q", "").strip()
    author = Author.query.get_or_404(author_id)

    books_count = Book.query.filter_by(author_id=author.id).count()

    if books_count:
        flash("Cannot delete author with associated books.", "danger")
    else:
        db.session.delete(author)
        db.session.commit()
        flash("Author deleted successfully.", "success")

    return redirect(url_for("librarian.manage_authors", q=q))


# =====================================================
# FACULTY MANAGEMENT
# =====================================================


@librarian_bp.route("/faculties", methods=["GET", "POST"])
def manage_faculties():
    form = FacultyForm()
    edit_form = FacultyForm(prefix="edit")
    q = request.args.get("q", "").strip()

    if form.validate_on_submit() and not request.form.get("edit_id"):
        faculty_name = form.name.data.strip()
        existing = Faculty.query.filter(Faculty.name.ilike(faculty_name)).first()
        if existing:
            flash("Faculty already exists.", "warning")
        else:
            faculty = Faculty(name=faculty_name)
            db.session.add(faculty)
            db.session.commit()
            flash("Faculty added successfully.", "success")
        return redirect(url_for("librarian.manage_faculties", q=q))

    faculties_query = Faculty.query
    if q:
        faculties_query = faculties_query.filter(Faculty.name.ilike(f"%{q}%"))

    faculties = faculties_query.order_by(Faculty.name.asc()).all()
    editing = None
    edit_id = request.args.get("edit", type=int)
    if edit_id:
        editing = Faculty.query.get_or_404(edit_id)
        edit_form.name.data = editing.name

    return render_template(
        "librarian/faculties.html",
        faculties=faculties,
        form=form,
        edit_form=edit_form,
        editing=editing,
        q=q,
    )


@librarian_bp.route("/faculties/<int:faculty_id>/edit", methods=["POST"])
def faculty_edit(faculty_id):
    q = request.args.get("q", "").strip()
    faculty = Faculty.query.get_or_404(faculty_id)
    form = FacultyForm(prefix="edit")

    if not form.validate_on_submit():
        flash("Could not update faculty. Check the form and try again.", "danger")
        return redirect(url_for("librarian.manage_faculties", q=q, edit=faculty_id))

    new_name = form.name.data.strip()
    duplicate = Faculty.query.filter(
        Faculty.id != faculty.id,
        Faculty.name.ilike(new_name),
    ).first()
    if duplicate:
        flash("Another faculty with this name already exists.", "warning")
        return redirect(url_for("librarian.manage_faculties", q=q, edit=faculty_id))

    faculty.name = new_name
    User.query.filter_by(faculty_id=faculty.id).update(
        {User.faculty: new_name},
        synchronize_session=False,
    )
    db.session.commit()
    flash("Faculty updated successfully.", "success")
    return redirect(url_for("librarian.manage_faculties", q=q))


@librarian_bp.route("/faculties/<int:faculty_id>/delete", methods=["POST"])
def faculty_delete(faculty_id):
    q = request.args.get("q", "").strip()
    faculty = Faculty.query.get_or_404(faculty_id)
    users_count = User.query.filter_by(faculty_id=faculty.id).count()

    if users_count:
        flash("Cannot delete faculty while users are assigned to it.", "danger")
    else:
        db.session.delete(faculty)
        db.session.commit()
        flash("Faculty deleted successfully.", "success")

    return redirect(url_for("librarian.manage_faculties", q=q))


# =====================================================
# USER MANAGEMENT
# =====================================================


@librarian_bp.route("/users")
def manage_users():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    faculty_id = request.args.get("faculty", type=int)

    query = User.query.filter_by(role=User.ROLE_USER)

    if q:
        query = query.filter(
            or_(
                User.username.ilike(f"%{q}%"),
                User.fullname.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
                User.phone_number.ilike(f"%{q}%"),
                User.group_name.ilike(f"%{q}%"),
                User.faculty.ilike(f"%{q}%"),
            )
        )

    if faculty_id:
        query = query.filter(User.faculty_id == faculty_id)

    pagination = query.order_by(desc(User.created_at)).paginate(
        page=page,
        per_page=20,
        error_out=False,
    )

    return render_template(
        "librarian/users.html",
        pagination=pagination,
        q=q,
        faculty_id=faculty_id,
        faculties=Faculty.query.order_by(Faculty.name.asc()).all(),
    )


@librarian_bp.route("/users/add", methods=["GET", "POST"])
def add_user():
    # preserve source/back_url for deterministic back navigation
    source = request.values.get("source", "librarian")
    if source not in BACK_URLS:
        source = "librarian"
    back_url = url_for(BACK_URLS[source])

    form = ManualUserForm()
    load_faculty_choices(form, include_empty=True)

    if not form.faculty_id.choices or form.faculty_id.choices == [(0, "Select faculty")]:
        flash("Add at least one faculty before creating users.", "warning")
        return redirect(url_for("librarian.manage_faculties"))

    created_password = None
    created_user = None

    if form.validate_on_submit():
        if form.faculty_id.data == 0:
            form.faculty_id.errors.append("Faculty is required.")
        else:
            try:
                created_user, created_password = create_user_account(
                    fullname=form.fullname.data,
                    email=form.email.data,
                    phone_number=form.phone_number.data,
                    faculty_id=form.faculty_id.data,
                    group_name=form.group_name.data,
                )
                log_activity(
                    current_user.id,
                    f"Created user account {created_user.username} ({created_user.fullname})",
                )
                flash("User account created successfully.", "success")
            except ValueError as exc:
                flash(str(exc), "danger")

    return render_template(
        "librarian/add_user.html",
        form=form,
        created_user=created_user,
        created_password=created_password,
        source=source,
        back_url=back_url,
    )


@librarian_bp.route("/users/import", methods=["GET", "POST"])
def import_users():
    # source may be provided as query param or posted in the form; prefer posted value on POST
    source = request.values.get("source", "librarian")
    if source not in BACK_URLS:
        source = "librarian"

    back_url = url_for(BACK_URLS[source])

    form = UserImportForm()
    load_faculty_choices(form, include_empty=False)

    if request.method == "GET":
        form.default_password.data = default_temp_password()

    if not form.faculty_id.choices:
        flash("Add at least one faculty before importing users.", "warning")
        return redirect(url_for("librarian.manage_faculties"))

    if form.validate_on_submit():
        upload = form.excel_file.data
        try:
            file_bytes = upload.read()
            preview = parse_excel_file(
                file_bytes,
                upload.filename,
                form.faculty_id.data,
            )
            token = secrets.token_urlsafe(16)
            session["user_import_preview"] = preview_to_session_dict(preview)
            session["user_import_token"] = token
            session["user_import_password"] = form.default_password.data
            return redirect(url_for("librarian.import_users_preview", token=token, source=source))
        except ValueError as exc:
            flash(str(exc), "danger")
        except Exception:
            flash("Could not read the Excel file. Check the format and try again.", "danger")

    return render_template("librarian/import_users.html", form=form, source=source, back_url=back_url)


@librarian_bp.route("/users/import/preview")
def import_users_preview():
    # preserve source param to compute back_url
    source = request.args.get("source", "librarian")
    if source not in BACK_URLS:
        source = "librarian"
    back_url = url_for(BACK_URLS[source])

    token = request.args.get("token", "")
    if not token or token != session.get("user_import_token"):
        flash("Import preview expired. Upload the file again.", "warning")
        return redirect(url_for("librarian.import_users", source=source))

    data = session.get("user_import_preview")
    if not data:
        flash("Import preview expired. Upload the file again.", "warning")
        return redirect(url_for("librarian.import_users", source=source))

    preview = preview_from_session_dict(data)
    default_password = session.get("user_import_password") or default_temp_password()
    return render_template(
        "librarian/import_preview.html",
        preview=preview,
        token=token,
        default_password=default_password,
        source=source,
        back_url=back_url,
    )


@librarian_bp.route("/users/import/confirm", methods=["POST"])
def import_users_confirm():
    # preserve source from posted form
    source = request.values.get("source", "librarian")
    if source not in BACK_URLS:
        source = "librarian"
    back_url = url_for(BACK_URLS[source])

    token = request.form.get("token", "")
    if not token or token != session.get("user_import_token"):
        flash("Import session expired. Upload the file again.", "warning")
        return redirect(url_for("librarian.import_users", source=source))

    data = session.get("user_import_preview")
    if not data:
        flash("Import session expired. Upload the file again.", "warning")
        return redirect(url_for("librarian.import_users", source=source))

    preview = preview_from_session_dict(data)
    if preview.valid_count == 0:
        flash("No valid rows to import.", "danger")
        return redirect(url_for("librarian.import_users", source=source))

    password = session.get("user_import_password")
    result = commit_import(preview, password=password)
    faculty_name = preview.faculty_name
    log_activity(
        current_user.id,
        (
            f"Imported {result.created} users for faculty {faculty_name} "
            f"({result.skipped} skipped of {result.processed} rows)"
        ),
    )

    session.pop("user_import_preview", None)
    session.pop("user_import_token", None)
    session.pop("user_import_password", None)
    report_token = secrets.token_urlsafe(16)
    session[f"import_report_{report_token}"] = {
        "rows": result.report_rows,
        "created": result.created,
        "skipped": result.skipped,
        "processed": result.processed,
        "faculty_name": faculty_name,
    }

    flash(
        f"Import complete: {result.created} users created, {result.skipped} skipped.",
        "success",
    )
    return redirect(
        url_for(
            "librarian.import_users_result",
            token=report_token,
            created=result.created,
            skipped=result.skipped,
            processed=result.processed,
            source=source,
        )
    )


@librarian_bp.route("/users/import/result")
def import_users_result():
    token = request.args.get("token", "")
    # preserve source param for back navigation
    source = request.args.get("source", "librarian")
    if source not in BACK_URLS:
        source = "librarian"
    back_url = url_for(BACK_URLS[source])

    report = session.get(f"import_report_{token}")
    if not report:
        flash("Import report expired.", "warning")
        return redirect(url_for(BACK_URLS.get(source, "librarian.manage_users")))

    return render_template(
        "librarian/import_result.html",
        report=report,
        token=token,
        created=request.args.get("created", type=int) or report.get("created", 0),
        skipped=request.args.get("skipped", type=int) or report.get("skipped", 0),
        processed=request.args.get("processed", type=int) or report.get("processed", 0),
        source=source,
        back_url=back_url,
    )


@librarian_bp.route("/users/import/report/<token>")
def import_users_report(token):
    report = session.get(f"import_report_{token}")
    if not report:
        flash("Import report expired.", "warning")
        return redirect(url_for("librarian.manage_users"))

    workbook = build_import_report_workbook(report.get("rows", []))
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="import_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
