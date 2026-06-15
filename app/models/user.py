from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from app.utils.datetime import now_local


class User(UserMixin, db.Model):
    __tablename__ = "users"

    ROLE_USER = "user"
    ROLE_LIBRARIAN = "librarian"
    ROLE_ADMIN = "admin"
    ROLE_SUPERADMIN = "superadmin"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(30), nullable=True, unique=True, index=True)
    faculty = db.Column(db.String(120), nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=True, index=True)
    group_name = db.Column(db.String(80), nullable=True)

    faculty_rel = db.relationship(
        "Faculty",
        back_populates="users",
        foreign_keys=[faculty_id],
    )
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_USER)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True) # Optional link to new Role table
    avatar = db.Column(db.String(255), nullable=True)

    email_verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    last_login_at = db.Column(
        db.DateTime,
        nullable=True
    )

    last_activity_at = db.Column(
        db.DateTime,
        nullable=True
    )

    is_blocked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=now_local)

    # Relationships
    borrow_requests = db.relationship("BorrowRequest", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    borrow_history = db.relationship("BorrowHistory", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    favorites = db.relationship("FavoriteBook", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    activities = db.relationship("ActivityLog", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    reading_progress = db.relationship("ReadingProgress", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    pdf_bookmarks = db.relationship("PDFBookmark", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:

        self.password_hash = generate_password_hash(

            password,

            method="pbkdf2:sha256",

            salt_length=16
        )

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


    # =====================================================
    # LOGIN TRACKING
    # =====================================================

    def update_last_login(self):

        self.last_login_at = now_local()

        self.last_activity_at = now_local()

        db.session.commit()


    def update_activity(self):

        self.last_activity_at = now_local()

        db.session.commit()

    @property
    def is_superadmin(self) -> bool:
        return self.role == self.ROLE_SUPERADMIN

    @property
    def is_admin(self) -> bool:
        # SuperAdmin has all admin capabilities
        return self.role in (self.ROLE_ADMIN, self.ROLE_SUPERADMIN)

    @property
    def is_librarian(self) -> bool:
        return self.role == self.ROLE_LIBRARIAN

    @property
    def is_staff(self) -> bool:
        return self.role in (self.ROLE_ADMIN, self.ROLE_LIBRARIAN, self.ROLE_SUPERADMIN)

    @property
    def faculty_display(self) -> str:
        if self.faculty_rel:
            return self.faculty_rel.name
        return self.faculty or ""

    def sync_faculty_name(self) -> None:
        if self.faculty_rel:
            self.faculty = self.faculty_rel.name
        elif self.faculty_id is None:
            self.faculty = None

    # =====================================================
    # RESET TOKEN
    # =====================================================

    def generate_reset_token(self):

        serializer = URLSafeTimedSerializer(
            current_app.config["SECRET_KEY"]
        )

        return serializer.dumps(
            self.email,
            salt="password-reset-salt"
        )


    # =====================================================
    # VERIFY RESET TOKEN
    # =====================================================

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):

        serializer = URLSafeTimedSerializer(
            current_app.config["SECRET_KEY"]
        )

        try:

            email = serializer.loads(

                token,

                salt="password-reset-salt",

                max_age=expires_sec
            )

        except Exception:

            return None

        return User.query.filter_by(
            email=email
        ).first()


    # =====================================================
    # EMAIL VERIFICATION TOKEN
    # =====================================================

    def generate_email_verification_token(self):

        serializer = URLSafeTimedSerializer(

            current_app.config["SECRET_KEY"]
        )

        return serializer.dumps(

            self.email,

            salt="email-verify-salt"
        )


    @staticmethod
    def verify_email_token(

        token,

        expires_sec=86400
    ):

        serializer = URLSafeTimedSerializer(

            current_app.config["SECRET_KEY"]
        )

        try:

            email = serializer.loads(

                token,

                salt="email-verify-salt",

                max_age=expires_sec
            )

        except Exception:

            return None

        return User.query.filter_by(
            email=email
        ).first()

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"
