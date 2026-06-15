from app import db
from app.utils.datetime import now_local


# =====================================================
# CATEGORY
# =====================================================

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    books = db.relationship(
        "Book",
        backref="category",
        lazy=True
    )

    def __repr__(self):
        return f"<Category {self.name}>"


# =====================================================
# AUTHOR
# =====================================================

class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    books = db.relationship(
        "Book",
        backref="author",
        lazy=True
    )

    def __repr__(self):
        return f"<Author {self.fullname}>"


# =====================================================
# BASE BOOK MODEL
# =====================================================

class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)

    # physical | digital
    book_type = db.Column(
        db.String(20),
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False,
        index=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    isbn = db.Column(
        db.String(30),
        nullable=True
    )

    language = db.Column(
        db.String(50),
        nullable=True
    )

    published_year = db.Column(
        db.Integer,
        nullable=True
    )

    cover_image = db.Column(
        db.String(255),
        nullable=True
    )

    rating = db.Column(
        db.Float,
        default=0.0
    )


    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    borrow_requests = db.relationship(
        "BorrowRequest",
        back_populates="book",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    borrow_history = db.relationship(
        "BorrowHistory",
        back_populates="book",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    favorites = db.relationship(
        "FavoriteBook",
        back_populates="book",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    reviews = db.relationship(
        "Review",
        backref="book",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id")
    )

    author_id = db.Column(
        db.Integer,
        db.ForeignKey("authors.id")
    )

    created_at = db.Column(
        db.DateTime,
        default=now_local
    )

    # polymorphism
    __mapper_args__ = {
        "polymorphic_on": book_type,
        "polymorphic_identity": "book"
    }

    def __repr__(self):
        return f"<Book {self.title}>"



# =====================================================
# PHYSICAL BOOK
# =====================================================

class PhysicalBook(Book):
    __tablename__ = "physical_books"

    id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        primary_key=True
    )

    quantity = db.Column(
        db.Integer,
        default=1
    )

    available_quantity = db.Column(
        db.Integer,
        default=1
    )

    borrow_count = db.Column(
        db.Integer,
        default=0
    )

    library_location = db.Column(
        db.String(120),
        nullable=True
    )

    shelf_code = db.Column(
        db.String(50),
        nullable=True
    )

    __mapper_args__ = {
        "polymorphic_identity": "physical"
    }


# =====================================================
# BOOK COPY (PHYSICAL COPIES)
# =====================================================

class BookCopy(db.Model):
    __tablename__ = "book_copies"

    id = db.Column(db.Integer, primary_key=True)

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    nn_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="available",  # available, borrowed, lost, damaged
        nullable=False
    )
    
    created_at = db.Column(
        db.DateTime,
        default=now_local
    )

    book = db.relationship("Book", backref=db.backref("copies", lazy="dynamic", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<BookCopy {self.nn_number} for Book:{self.book_id}>"



# =====================================================
# DIGITAL BOOK
# =====================================================

class DigitalBook(Book):
    __tablename__ = "digital_books"

    id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        primary_key=True
    )

    pdf_file = db.Column(
        db.String(255),
        nullable=False
    )

    pages = db.Column(
        db.Integer,
        nullable=True
    )

    file_size = db.Column(
        db.Integer,
        nullable=True
    )

    # Total opens (view_count) — incremented every session regardless of user
    view_count = db.Column(
        db.Integer,
        default=0
    )

    # Legacy column — kept for schema compatibility; no longer written
    reading_count = db.Column(
        db.Integer,
        default=0
    )

    allow_download = db.Column(
        db.Boolean,
        default=False
    )

    online_read_only = db.Column(
        db.Boolean,
        default=False
    )

    reading_progress_records = db.relationship("ReadingProgress", backref="digital_book", cascade="all, delete-orphan", lazy="dynamic")
    bookmarks = db.relationship("PDFBookmark", backref="digital_book", cascade="all, delete-orphan", lazy="dynamic")
    book_reads = db.relationship("BookRead", backref="digital_book", cascade="all, delete-orphan", lazy="dynamic")

    __mapper_args__ = {
        "polymorphic_identity": "digital"
    }

    @property
    def reader_count(self):
        return self.book_reads.count()



# =====================================================
# READING PROGRESS
# =====================================================

class ReadingProgress(db.Model):
    __tablename__ = "reading_progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("digital_books.id", ondelete="CASCADE"),
        nullable=False
    )

    current_page = db.Column(
        db.Integer,
        default=1
    )

    updated_at = db.Column(
        db.DateTime,
        default=now_local
    )



# =====================================================
# PDF BOOKMARKS
# =====================================================

class PDFBookmark(db.Model):
    __tablename__ = "pdf_bookmarks"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("digital_books.id", ondelete="CASCADE"),
        nullable=False
    )

    page_number = db.Column(
        db.Integer,
        nullable=False
    )

    note = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=now_local
    )


# =====================================================
# BOOK READ TRACKING (unique readers)
# =====================================================

class BookRead(db.Model):
    """One row per (user, digital book) pair — tracks unique readers."""
    __tablename__ = "book_reads"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("digital_books.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    first_read_at = db.Column(
        db.DateTime,
        default=now_local,
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "book_id", name="uq_book_read_user_book"),
    )

    def __repr__(self):
        return f"<BookRead user={self.user_id} book={self.book_id}>"
