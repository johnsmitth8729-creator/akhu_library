import os
from datetime import timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
    send_from_directory,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from sqlalchemy import or_, func

from app import db

from app.models.book import (
    Book,
    PhysicalBook,
    DigitalBook,
    Category,
    ReadingProgress,
    PDFBookmark,
    BookRead
)

from app.models.borrow import (
    BorrowRequest,
    BorrowHistory,
    FavoriteBook
)

from app.models.system import (
    Notification,
    Review,
    Settings
)
from app.models.user import User
from app.utils.datetime import now_local
from app.utils.helpers import (
    get_int_setting,
    get_setting_value,
    send_library_status_email
)
from app.services.digital_rights import (
    can_download_digital_book,
    issue_reader_access,
    validate_reader_pdf_access,
)


def promote_waiting_request(book_id):
    queued_request = BorrowRequest.query.filter_by(
        book_id=book_id,
        status="Queued"
    ).order_by(
        BorrowRequest.request_date.asc()
    ).first()

    if not queued_request:
        return

    queued_request.status = "Pending"

    db.session.add(Notification(
        user_id=queued_request.user_id,
        type="info",
        message=(
            f"A copy of '{queued_request.book.title}' is now available. "
            "Your waiting list request has moved into librarian review."
        )
    ))

    librarians = User.query.filter(User.role.in_([User.ROLE_LIBRARIAN, User.ROLE_ADMIN])).all()
    for librarian in librarians:
        db.session.add(Notification(
            user_id=librarian.id,
            type="info",
            message=f"Queued request for '{queued_request.book.title}' by {queued_request.user.fullname} moved to pending."
        ))

    if queued_request.user:
        send_library_status_email(
            queued_request.user,
            "Waiting List Update",
            f"A copy of '{queued_request.book.title}' is now available.",
            [
                "Your waiting list request has moved into librarian review.",
                "Please check your account notifications for the latest request status."
            ]
        )


books_bp = Blueprint(
    "books",
    __name__
)


@books_bp.route("/")
def index():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    search = request.args.get(
        "q",
        ""
    ).strip()

    category_id = request.args.get(
        "category",
        type=int
    )

    book_type = request.args.get(
        "type",
        ""
    ).strip()

    query = Book.query

    if search:

        query = query.filter(

            or_(

                Book.title.ilike(
                    f"%{search}%"
                ),

                Book.isbn.ilike(
                    f"%{search}%"
                )

            )

        )

    if category_id:

        query = query.filter(
            Book.category_id == category_id
        )

    if book_type in ["physical", "digital"]:

        query = query.filter(
            Book.book_type == book_type
        )

    pagination = query.order_by(
        Book.created_at.desc()
    ).paginate(
        page=page,
        per_page=current_app.config.get(
            "ITEMS_PER_PAGE",
            12
        ),
        error_out=False
    )

    categories = Category.query.order_by(
        Category.name.asc()
    ).all()

    return render_template(
        "books/index.html",
        pagination=pagination,
        categories=categories,
        search=search,
        current_category=category_id,
        book_type=book_type
    )


@books_bp.route("/<int:book_id>")
def detail(book_id):

    book = Book.query.get_or_404(
        book_id
    )

    is_favorite = False
    user_pending_request = None
    user_queued_request = None
    user_active_borrow = None

    reviews = Review.query.filter_by(
        book_id=book.id
    ).order_by(
        Review.created_at.desc()
    ).all()

    if current_user.is_authenticated:

        is_favorite = FavoriteBook.query.filter_by(
            user_id=current_user.id,
            book_id=book.id
        ).first() is not None

        if book.book_type == "physical":

            user_pending_request = BorrowRequest.query.filter_by(
                user_id=current_user.id,
                book_id=book.id,
                status="Pending"
            ).first()

            user_queued_request = BorrowRequest.query.filter_by(
                user_id=current_user.id,
                book_id=book.id,
                status="Queued"
            ).first()

            user_active_borrow = BorrowHistory.query.filter(
                BorrowHistory.user_id == current_user.id,
                BorrowHistory.book_id == book.id,
                BorrowHistory.status.in_(
                    ["Borrowed", "Overdue"]
                )
            ).first()

    can_download = False
    unique_readers = None
    if book.book_type == "digital":
        can_download = can_download_digital_book(book)
        unique_readers = db.session.query(func.count(func.distinct(BookRead.user_id))).filter(BookRead.book_id == book.id).scalar()

    return render_template(
        "books/detail.html",
        book=book,
        reviews=reviews,
        is_favorite=is_favorite,
        user_pending_request=user_pending_request,
        user_active_borrow=user_active_borrow,
        user_queued_request=user_queued_request if current_user.is_authenticated and book.book_type == "physical" else None,
        can_download_digital=can_download,
        unique_readers=unique_readers,
    )


@books_bp.route(
    "/<int:book_id>/request",
    methods=["POST"]
)
@login_required
def request_borrow(book_id):

    book = PhysicalBook.query.get_or_404(
        book_id
    )

    if current_user.is_blocked:
        flash(
            "Your account is blocked. Contact the library staff for assistance.",
            "danger"
        )
        return redirect(
            url_for(
                "books.detail",
                book_id=book.id
            )
        )

    block_unpaid_fines = str(
        get_setting_value("block_unpaid_fines", "True")
    ).lower() == "true"

    if block_unpaid_fines and BorrowHistory.query.filter(
        BorrowHistory.user_id == current_user.id,
        BorrowHistory.fine_status == "unpaid",
        BorrowHistory.final_fine_amount > 0
    ).count():
        flash(
            "You have unpaid fines. Please settle them before requesting more books.",
            "warning"
        )
        return redirect(
            url_for(
                "books.detail",
                book_id=book.id
            )
        )

    daily_request_limit = get_int_setting(
        "daily_request_limit",
        current_app.config.get("DAILY_REQUEST_LIMIT", 5)
    )

    day_start = now_local().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )
    day_end = day_start + timedelta(days=1)

    today_request_count = BorrowRequest.query.filter(
        BorrowRequest.user_id == current_user.id,
        BorrowRequest.request_date >= day_start,
        BorrowRequest.request_date < day_end
    ).count()

    if today_request_count >= daily_request_limit:
        flash(
            f"You have reached the daily request limit of {daily_request_limit}.",
            "warning"
        )
        return redirect(
            url_for(
                "books.detail",
                book_id=book.id
            )
        )

    existing_request = BorrowRequest.query.filter(
        BorrowRequest.user_id == current_user.id,
        BorrowRequest.book_id == book.id,
        BorrowRequest.status.in_(["Pending", "Queued"])
    ).first()

    if existing_request:

        flash(
            "You already have an active request for this book.",
            "warning"
        )

        return redirect(
            url_for(
                "books.detail",
                book_id=book.id
            )
        )

    existing_active_borrow = BorrowHistory.query.filter(
        BorrowHistory.user_id == current_user.id,
        BorrowHistory.book_id == book.id,
        BorrowHistory.status.in_(
            ["Borrowed", "Overdue"]
        )
    ).first()

    if existing_active_borrow:

        flash(
            "You already borrowed this book.",
            "warning"
        )

        return redirect(
            url_for(
                "books.detail",
                book_id=book.id
            )
        )

    max_active_borrows = get_int_setting(
        "max_active_borrows",
        current_app.config.get("MAX_ACTIVE_BORROWS", 5)
    )

    active_borrow_count = BorrowHistory.query.filter(
        BorrowHistory.user_id == current_user.id,
        BorrowHistory.status.in_(
            ["Borrowed", "Overdue"]
        )
    ).count()

    if active_borrow_count >= max_active_borrows:

        flash(
            f"You can only have {max_active_borrows} active borrowed books.",
            "warning"
        )

        return redirect(
            url_for(
                "books.detail",
                book_id=book.id
            )
        )

    request_status = "Pending" if book.available_quantity > 0 else "Queued"

    if request_status == "Queued":
        max_waiting_list_requests = get_int_setting(
            "max_waiting_list_requests",
            current_app.config.get("MAX_WAITING_LIST_REQUESTS", 3)
        )

        queued_request_count = BorrowRequest.query.filter(
            BorrowRequest.user_id == current_user.id,
            BorrowRequest.status == "Queued"
        ).count()

        if queued_request_count >= max_waiting_list_requests:
            flash(
                f"You can only keep {max_waiting_list_requests} books in the waiting list at once.",
                "warning"
            )
            return redirect(
                url_for(
                    "books.detail",
                    book_id=book.id
                )
            )

    borrow_request = BorrowRequest(
        user_id=current_user.id,
        book_id=book.id,
        status=request_status
    )

    notification = Notification(
        user_id=current_user.id,
        type="info",
        message=(
            f"Borrow request for '{book.title}' sent successfully."
            if request_status == "Pending"
            else f"You joined the waiting list for '{book.title}'."
        )
    )

    db.session.add(
        borrow_request
    )

    db.session.add(
        notification
    )

    librarians = User.query.filter(User.role.in_([User.ROLE_LIBRARIAN, User.ROLE_ADMIN])).all()
    for librarian in librarians:
        lib_notification = Notification(
            user_id=librarian.id,
            type="info",
            message=(
                f"New borrow request for '{book.title}' from {current_user.fullname}."
                if request_status == "Pending"
                else f"{current_user.fullname} joined the waiting list for '{book.title}'."
            )
        )
        db.session.add(lib_notification)

    db.session.commit()

    try:
        from app.utils.telegram import send_telegram_notification
        send_telegram_notification(
            f"📚 <b>Yangi buyurtma so'rovi yuborildi:</b>\n"
            f"Foydalanuvchi: {current_user.fullname}\n"
            f"Kitob: {book.title}\n"
            f"Holati: {'Navbatda (Waiting List)' if request_status == 'Queued' else 'Kutishda (Pending Review)'}"
        )
    except Exception:
        pass

    send_library_status_email(
        current_user,
        "Library Request Update",
        (
            f"Your borrow request for '{book.title}' has been submitted."
            if request_status == "Pending"
            else f"You joined the waiting list for '{book.title}'."
        ),
        [
            "A librarian will review your request once the request becomes active."
            if request_status == "Pending"
            else "You will be notified automatically when a copy becomes available."
        ]
    )

    flash(
        "Borrow request sent successfully."
        if request_status == "Pending"
        else "Book unavailable. You were added to the waiting list.",
        "success" if request_status == "Pending" else "info"
    )

    return redirect(
        url_for(
            "books.detail",
            book_id=book.id
        )
    )


@books_bp.route(
    "/<int:book_id>/favorite",
    methods=["POST"]
)
@login_required
def toggle_favorite(book_id):

    book = Book.query.get_or_404(
        book_id
    )

    existing_favorite = FavoriteBook.query.filter_by(
        user_id=current_user.id,
        book_id=book.id
    ).first()

    if existing_favorite:

        db.session.delete(
            existing_favorite
        )

        db.session.commit()

        flash(
            "Removed from favorites.",
            "info"
        )

    else:

        favorite = FavoriteBook(
            user_id=current_user.id,
            book_id=book.id
        )

        db.session.add(
            favorite
        )

        db.session.commit()

        flash(
            "Added to favorites.",
            "success"
        )

    return redirect(
        request.referrer or url_for(
            "books.detail",
            book_id=book.id
        )
    )


@books_bp.route(
    "/digital/<int:book_id>/read"
)
@login_required
def read_digital_book(book_id):

    book = DigitalBook.query.get_or_404(
        book_id
    )

    # Increment total views every open (regardless of user)
    book.view_count = (book.view_count or 0) + 1

    # Track unique reader — insert once per user per book
    already_read = BookRead.query.filter_by(
        user_id=current_user.id,
        book_id=book.id
    ).first()
    if not already_read:
        db.session.add(BookRead(
            user_id=current_user.id,
            book_id=book.id
        ))

    progress = ReadingProgress.query.filter_by(
        user_id=current_user.id,
        book_id=book.id
    ).first()

    if not progress:

        progress = ReadingProgress(
            user_id=current_user.id,
            book_id=book.id,
            current_page=1
        )

        db.session.add(
            progress
        )

    db.session.commit()

    access_token = issue_reader_access(current_user.id, book.id)
    pdf_url = url_for("books.pdf", book_id=book.id, access=access_token)

    return render_template(
        "books/reader.html",
        book=book,
        progress=progress,
        pdf_url=pdf_url,
        read_protected=bool(book.online_read_only),
        allow_download=can_download_digital_book(book),
    )



@books_bp.route("/digital/<int:book_id>/pdf")
@login_required
def pdf(book_id):

    book = DigitalBook.query.get_or_404(book_id)

    if not book.pdf_file:
        abort(404)

    token = request.args.get("access")
    if not validate_reader_pdf_access(book_id, token):
        abort(403)

    pdf_path = os.path.join(
        current_app.static_folder,
        book.pdf_file
    )

    directory = os.path.dirname(pdf_path)

    filename = os.path.basename(pdf_path)

    response = send_from_directory(
        directory,
        filename,
        mimetype="application/pdf"
    )

    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    return response



@books_bp.route(
    "/digital/<int:book_id>/download"
)
@login_required
def download_digital_book(book_id):

    book = DigitalBook.query.get_or_404(
        book_id
    )

    if not can_download_digital_book(book):

        if book.online_read_only:
            message = "This book is available for online reading only."
        else:
            message = "Download is disabled for this digital book."

        flash(message, "danger")

        return redirect(
            url_for(
                "books.detail",
                book_id=book.id
            )
        )

    if not book.pdf_file:

        flash(
            "PDF not found.",
            "danger"
        )

        return redirect(
            url_for(
                "books.detail",
                book_id=book.id
            )
        )

    static_root = os.path.join(
        current_app.root_path,
        "static"
    )

    return send_from_directory(
        static_root,
        book.pdf_file,
        as_attachment=True
    )


@books_bp.route(
    "/digital/<int:book_id>/progress",
    methods=["GET", "POST"]
)
@login_required
def digital_book_progress(book_id):

    book = DigitalBook.query.get_or_404(
        book_id
    )

    progress = ReadingProgress.query.filter_by(
        user_id=current_user.id,
        book_id=book.id
    ).first()

    if request.method == "POST":

        payload = request.get_json(silent=True) or {}

        page = payload.get(
            "page",
            request.form.get(
                "page",
                type=int
            )
        )

        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        page = max(1, page)

        if not progress:
            progress = ReadingProgress(
                user_id=current_user.id,
                book_id=book.id
            )
            db.session.add(progress)

        progress.current_page = page
        progress.updated_at = now_local()
        db.session.commit()

        return {
            "success": True,
            "current_page": progress.current_page
        }

    return {
        "success": True,
        "current_page": progress.current_page if progress else 1
    }


@books_bp.route(
    "/digital/<int:book_id>/bookmark",
    methods=["POST"]
)
@login_required
def bookmark_digital_book(book_id):

    book = DigitalBook.query.get_or_404(
        book_id
    )

    payload = request.get_json(silent=True) or {}
    page = payload.get(
        "page",
        request.form.get(
            "page",
            type=int
        )
    )

    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    page = max(1, page)

    bookmark = PDFBookmark.query.filter_by(
        user_id=current_user.id,
        book_id=book.id,
        page_number=page
    ).first()

    if not bookmark:
        bookmark = PDFBookmark(
            user_id=current_user.id,
            book_id=book.id,
            page_number=page
        )
        db.session.add(bookmark)
        db.session.commit()

    return {
        "success": True,
        "page": bookmark.page_number
    }


@books_bp.route("/favorites")
@login_required
def favorites():

    favorites = FavoriteBook.query.filter_by(
        user_id=current_user.id
    ).order_by(
        FavoriteBook.created_at.desc()
    ).all()

    return render_template(
        "books/favorites.html",
        favorites=favorites
    )


@books_bp.route("/my-requests")
@login_required
def my_requests():

    borrow_requests = BorrowRequest.query.filter_by(
        user_id=current_user.id
    ).order_by(
        BorrowRequest.request_date.desc()
    ).all()

    return render_template(
        "books/my_requests.html",
        requests=borrow_requests
    )


@books_bp.route("/my-borrowed")
@login_required
def my_borrowed_books():

    borrowings = BorrowHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        BorrowHistory.borrowed_at.desc()
    ).all()

    return render_template(
        "books/my_borrowed.html",
        borrowings=borrowings
    )


@books_bp.route(
    "/<int:book_id>/review",
    methods=["POST"]
)
@login_required
def add_review(book_id):

    book = Book.query.get_or_404(
        book_id
    )

    rating = request.form.get(
        "rating",
        type=int
    )

    comment = request.form.get(
        "comment",
        ""
    ).strip()

    if not rating or rating < 1 or rating > 5:

        flash(
            "Invalid rating.",
            "danger"
        )

        return redirect(
            url_for(
                "books.detail",
                book_id=book.id
            )
        )

    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        book_id=book.id
    ).first()

    if existing_review:

        existing_review.rating = rating
        existing_review.comment = comment

        flash(
            "Review updated.",
            "success"
        )

    else:

        review = Review(
            user_id=current_user.id,
            book_id=book.id,
            rating=rating,
            comment=comment
        )

        db.session.add(
            review
        )

        flash(
            "Review added.",
            "success"
        )

    db.session.commit()

    update_book_rating(
        book.id
    )

    return redirect(
        url_for(
            "books.detail",
            book_id=book.id
        )
    )


@books_bp.route(
    "/review/<int:review_id>/delete",
    methods=["POST"]
)
@login_required
def delete_review(review_id):

    review = Review.query.get_or_404(
        review_id
    )

    if review.user_id != current_user.id:

        flash(
            "Unauthorized.",
            "danger"
        )

        return redirect(
            url_for(
                "books.detail",
                book_id=review.book_id
            )
        )

    book_id = review.book_id

    db.session.delete(
        review
    )

    db.session.commit()

    update_book_rating(
        book_id
    )

    flash(
        "Review deleted.",
        "info"
    )

    return redirect(
        url_for(
            "books.detail",
            book_id=book_id
        )
    )


def update_book_rating(book_id):

    book = Book.query.get(
        book_id
    )

    if not book:
        return

    reviews = Review.query.filter_by(
        book_id=book.id
    ).all()

    if not reviews:

        book.rating = 0

    else:

        total = sum(
            review.rating
            for review in reviews
        )

        book.rating = round(
            total / len(reviews),
            1
        )

    db.session.commit()
