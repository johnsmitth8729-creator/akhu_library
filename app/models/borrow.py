from app import db
from app.utils.datetime import now_local


class BorrowRequest(db.Model):
    __tablename__ = "borrow_requests"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    request_date = db.Column(
        db.DateTime,
        default=now_local,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Pending",
        nullable=False
    )

    book = db.relationship("Book", back_populates="borrow_requests")

    @property
    def waiting_position(self):
        if self.status != "Queued":
            return None

        return BorrowRequest.query.filter(
            BorrowRequest.book_id == self.book_id,
            BorrowRequest.status == "Queued",
            BorrowRequest.request_date <= self.request_date
        ).count()

    def __repr__(self):
        return f"<BorrowRequest {self.id} User:{self.user_id} Book:{self.book_id} Status:{self.status}>"


class BorrowHistory(db.Model):
    __tablename__ = "borrow_history"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    copy_id = db.Column(
        db.Integer,
        db.ForeignKey("book_copies.id"),
        nullable=True
    )

    borrowed_at = db.Column(
        db.DateTime,
        default=now_local,
        nullable=False
    )

    return_date = db.Column(
        db.DateTime,
        nullable=False
    )

    returned_at = db.Column(
        db.DateTime,
        nullable=True
    )

    final_fine_amount = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    fine_status = db.Column(
        db.String(20),
        default="none",
        nullable=False
    )

    return_condition = db.Column(
        db.String(20),
        default="good",
        nullable=False
    )

    condition_notes = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="Borrowed",
        nullable=False
    )

    book = db.relationship("Book", back_populates="borrow_history")
    copy = db.relationship("BookCopy", backref="borrow_records")

    @property
    def is_overdue(self):
        if self.status == "Returned":
            return False

        return now_local() > self.return_date

    def overdue_days(self, reference_time=None):
        effective_time = reference_time or self.returned_at or now_local()

        if effective_time <= self.return_date:
            return 0

        date_gap = (
            effective_time.date() - self.return_date.date()
        ).days

        return max(date_gap, 1)

    def fine_amount(self, daily_rate, reference_time=None):
        if not daily_rate:
            return 0

        return self.overdue_days(reference_time=reference_time) * max(daily_rate, 0)

    @property
    def has_unpaid_fine(self):
        return (self.final_fine_amount or 0) > 0 and self.fine_status == "unpaid"

    def __repr__(self):
        return f"<BorrowHistory {self.id} User:{self.user_id} Book:{self.book_id} Status:{self.status}>"


class FavoriteBook(db.Model):
    __tablename__ = "favorite_books"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=now_local,
        nullable=False
    )

    book = db.relationship("Book", back_populates="favorites")

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_user_book_fav"
        ),
    )

    def __repr__(self):
        return f"<FavoriteBook {self.id} User:{self.user_id} Book:{self.book_id}>"
