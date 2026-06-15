from app import db
from app.models.user import User
from app.models.faculty import Faculty
from app.models.book import Category, Author, Book, PhysicalBook, BookCopy
from app.models.role import Role
from app.models.system import Settings


def seed_initial_data():
    """Create default admin and a few categories/authors/books if empty."""
    default_roles = {
        "user": "Default library member",
        "librarian": "Library staff member",
        "admin": "System administrator"
    }

    for role_name, description in default_roles.items():
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(
                Role(
                    name=role_name,
                    description=description
                )
            )

    default_settings = {
        "library_name": ("Al-Khwarizmi Smart Library", "Portal header title displayed to all users"),
        "default_borrow_days": ("14", "Default duration (days) for a physical book borrow loan"),
        "max_active_borrows": ("5", "Maximum number of books a student can borrow at once"),
        "late_fine_per_day": ("1000", "Fine in UZS charged per day for overdue books"),
        "daily_request_limit": ("5", "Maximum number of borrow requests a user can submit per day"),
        "max_waiting_list_requests": ("3", "Maximum number of queued waiting-list requests per user"),
        "block_unpaid_fines": ("True", "Block new requests while unpaid fines exist (True/False)"),
        "allow_registration": ("True", "Allow public sign-ups on the registration page (True/False)"),
        "allow_digital_downloads": ("True", "Enable or disable digital PDF downloading globally (True/False)")
    }

    for key, (value, description) in default_settings.items():
        if not Settings.query.filter_by(key=key).first():
            db.session.add(
                Settings(
                    key=key,
                    value=value,
                    description=description
                )
            )

    default_faculty_name = "Computer Engineering"
    faculty = Faculty.query.filter_by(name=default_faculty_name).first()
    if not faculty:
        faculty = Faculty(name=default_faculty_name)
        db.session.add(faculty)
        db.session.flush()

    if not User.query.filter_by(role="admin").first():
        admin = User(
            fullname="System Administrator",
            username="admin",
            email="admin@alkhwarizmi.edu",
            group_name="ADMIN",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)

        librarian = User(
            fullname="Head Librarian",
            username="librarian",
            email="librarian@alkhwarizmi.edu",
            role="librarian",
        )
        librarian.set_password("librarian123")
        db.session.add(librarian)

    if Category.query.count() == 0:
        for name in ["Mathematics", "Computer Science", "Physics", "Literature",
                     "History", "Engineering", "Philosophy", "Medicine"]:
            db.session.add(Category(name=name))

    if Author.query.count() == 0:
        for name in ["Al-Khwarizmi", "Ibn Sina", "Donald Knuth", "Isaac Newton",
                     "Leo Tolstoy", "Marie Curie"]:
            db.session.add(Author(fullname=name))

    db.session.commit()

    if Book.query.count() == 0:
        cat_cs = Category.query.filter_by(name="Computer Science").first()
        cat_math = Category.query.filter_by(name="Mathematics").first()
        a_knuth = Author.query.filter_by(fullname="Donald Knuth").first()
        a_kh = Author.query.filter_by(fullname="Al-Khwarizmi").first()

        samples = [
            dict(
                book=dict(
                    book_type="physical",
                    title="The Art of Computer Programming",
                    isbn="978-0201896831",
                    description="A comprehensive monograph on algorithms and analysis.",
                    category_id=cat_cs.id if cat_cs else None,
                    author_id=a_knuth.id if a_knuth else None,
                    quantity=5,
                    available_quantity=5,
                ),
                nn_prefix="NN-001",
            ),
            dict(
                book=dict(
                    book_type="physical",
                    title="Algebra (Al-Jabr)",
                    isbn="978-0000000001",
                    description="The foundational text of algebra by Al-Khwarizmi.",
                    category_id=cat_math.id if cat_math else None,
                    author_id=a_kh.id if a_kh else None,
                    quantity=3,
                    available_quantity=3,
                ),
                nn_prefix="NN-002",
            ),
            dict(
                book=dict(
                    book_type="physical",
                    title="Introduction to Algorithms",
                    isbn="978-0262033848",
                    description="A standard text on algorithms used in universities worldwide.",
                    category_id=cat_cs.id if cat_cs else None,
                    author_id=a_knuth.id if a_knuth else None,
                    quantity=4,
                    available_quantity=4,
                ),
                nn_prefix="NN-003",
            ),
        ]
        for sample in samples:
            book = PhysicalBook(**sample["book"])
            db.session.add(book)
            db.session.flush()

            for copy_index in range(1, (book.quantity or 0) + 1):
                db.session.add(
                    BookCopy(
                        book_id=book.id,
                        nn_number=f"{sample['nn_prefix']}-{copy_index:02d}",
                        status="available",
                    )
                )
        db.session.commit()
