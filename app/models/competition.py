"""Reading competition models."""

from __future__ import annotations

import secrets

from app import db
from app.utils.datetime import now_local


class ReadingCompetition(db.Model):
    __tablename__ = "reading_competitions"

    TYPE_SINGLE_BOOK = "single_book"
    TYPE_MULTIPLE_BOOKS = "multiple_books"
    TYPE_FACULTY = "faculty"
    TYPE_GROUP = "group"
    TYPE_UNIVERSITY = "university"

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CLOSED = "closed"
    STATUS_ARCHIVED = "archived"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    competition_type = db.Column(db.String(30), nullable=False, default=TYPE_UNIVERSITY)
    status = db.Column(db.String(20), nullable=False, default=STATUS_DRAFT)
    visibility = db.Column(db.String(20), nullable=False, default="public")

    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    max_attempts = db.Column(db.Integer, nullable=False, default=1)
    passing_score = db.Column(db.Integer, nullable=False, default=60)
    time_limit_minutes = db.Column(db.Integer, nullable=True)
    top_winners_count = db.Column(db.Integer, nullable=False, default=3)

    randomize_questions = db.Column(db.Boolean, default=True, nullable=False)
    randomize_answers = db.Column(db.Boolean, default=True, nullable=False)
    prevent_reopen_completed = db.Column(db.Boolean, default=True, nullable=False)

    secure_quiz_mode = db.Column(db.Boolean, default=True, nullable=False)
    enable_watermark = db.Column(db.Boolean, default=True, nullable=False)
    disable_copy = db.Column(db.Boolean, default=True, nullable=False)
    disable_print = db.Column(db.Boolean, default=True, nullable=False)
    require_fullscreen = db.Column(db.Boolean, default=False, nullable=False)
    track_focus_loss = db.Column(db.Boolean, default=True, nullable=False)
    track_devtools = db.Column(db.Boolean, default=True, nullable=False)

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=now_local, nullable=False)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local, nullable=False)

    creator = db.relationship("User", foreign_keys=[created_by_id])
    books = db.relationship(
        "CompetitionBook",
        back_populates="competition",
        cascade="all, delete-orphan",
    )
    faculty_restrictions = db.relationship(
        "CompetitionFaculty",
        back_populates="competition",
        cascade="all, delete-orphan",
    )
    group_restrictions = db.relationship(
        "CompetitionGroup",
        back_populates="competition",
        cascade="all, delete-orphan",
    )
    competition_questions = db.relationship(
        "CompetitionQuestion",
        back_populates="competition",
        cascade="all, delete-orphan",
        order_by="CompetitionQuestion.sort_order",
    )
    attempts = db.relationship(
        "QuizAttempt",
        back_populates="competition",
        cascade="all, delete-orphan",
    )

    @property
    def faculties(self):
        return self.faculty_restrictions

    @property
    def groups(self):
        return self.group_restrictions

    @property
    def questions(self):
        return self.competition_questions

    @property
    def is_active(self) -> bool:
        return (
            self.status == self.STATUS_PUBLISHED
            and self.start_date <= now_local() <= self.end_date
        )

    @property
    def lifecycle_status(self) -> str:
        if self.status == self.STATUS_ARCHIVED:
            return "archived"
        if self.status == self.STATUS_DRAFT:
            return "draft"
        if self.is_upcoming:
            return "upcoming"
        if self.is_active:
            return "active"
        return "ended"

    @property
    def is_finished(self) -> bool:
        return now_local() > self.end_date

    @property
    def is_upcoming(self) -> bool:
        return now_local() < self.start_date

    @property
    def question_count(self) -> int:
        return len(self.competition_questions)

    @property
    def total_points(self) -> int:
        return sum(
            (cq.points_override or cq.question.points)
            for cq in self.competition_questions
            if cq.question
        )

    def __repr__(self) -> str:
        return f"<ReadingCompetition {self.id} {self.title}>"


class CompetitionBook(db.Model):
    __tablename__ = "competition_books"
    __table_args__ = (
        db.UniqueConstraint("competition_id", "book_id", name="uq_competition_book"),
    )

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("reading_competitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)

    competition = db.relationship("ReadingCompetition", back_populates="books")
    book = db.relationship("Book")


class CompetitionFaculty(db.Model):
    __tablename__ = "competition_faculties"
    __table_args__ = (
        db.UniqueConstraint("competition_id", "faculty_id", name="uq_competition_faculty"),
    )

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("reading_competitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)

    competition = db.relationship("ReadingCompetition", back_populates="faculty_restrictions")
    faculty = db.relationship("Faculty")


class CompetitionGroup(db.Model):
    __tablename__ = "competition_groups"
    __table_args__ = (
        db.UniqueConstraint("competition_id", "group_name", name="uq_competition_group"),
    )

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("reading_competitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    group_name = db.Column(db.String(100), nullable=False)

    competition = db.relationship("ReadingCompetition", back_populates="group_restrictions")


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_ABANDONED = "abandoned"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("reading_competitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    attempt_number = db.Column(db.Integer, default=1, nullable=False)
    status = db.Column(db.String(20), default=STATUS_IN_PROGRESS, nullable=False)

    started_at = db.Column(db.DateTime, default=now_local, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    correct_count = db.Column(db.Integer, default=0, nullable=False)
    wrong_count = db.Column(db.Integer, default=0, nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    max_score = db.Column(db.Integer, default=0, nullable=False)
    percentage = db.Column(db.Float, default=0.0, nullable=False)
    completion_seconds = db.Column(db.Integer, nullable=True)
    ranking_score = db.Column(db.Float, default=0.0, nullable=False)
    rank_position = db.Column(db.Integer, nullable=True)
    medal = db.Column(db.String(20), nullable=True)

    focus_loss_count = db.Column(db.Integer, default=0, nullable=False)
    fullscreen_exit_count = db.Column(db.Integer, default=0, nullable=False)
    violation_count = db.Column(db.Integer, default=0, nullable=False)
    question_order_json = db.Column(db.Text, nullable=True)

    user = db.relationship("User", backref=db.backref("quiz_attempts", lazy="dynamic"))
    competition = db.relationship("ReadingCompetition", back_populates="attempts")
    answers = db.relationship(
        "QuizAttemptAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )
    violations = db.relationship(
        "QuizViolation",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )
    certificate = db.relationship(
        "CompetitionCertificate",
        back_populates="attempt",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def passed(self) -> bool:
        return self.percentage >= (self.competition.passing_score if self.competition else 0)


class QuizAttemptAnswer(db.Model):
    __tablename__ = "quiz_attempt_answers"
    __table_args__ = (
        db.UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question"),
    )

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    selected_option_ids = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    points_earned = db.Column(db.Integer, default=0, nullable=False)
    options_order_json = db.Column(db.Text, nullable=True)

    attempt = db.relationship("QuizAttempt", back_populates="answers")
    question = db.relationship("Question")


class QuizViolation(db.Model):
    __tablename__ = "quiz_violations"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=now_local, nullable=False)

    attempt = db.relationship("QuizAttempt", back_populates="violations")


class UserBadge(db.Model):
    __tablename__ = "user_badges"

    BADGE_GOLD = "gold"
    BADGE_SILVER = "silver"
    BADGE_BRONZE = "bronze"
    BADGE_READER = "reader"
    BADGE_PARTICIPANT = "participant"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("reading_competitions.id", ondelete="SET NULL"),
        nullable=True,
    )
    badge_type = db.Column(db.String(30), nullable=False)
    label = db.Column(db.String(120), nullable=False)
    awarded_at = db.Column(db.DateTime, default=now_local, nullable=False)

    user = db.relationship("User", backref=db.backref("badges", lazy="dynamic"))
    competition = db.relationship("ReadingCompetition")


class CompetitionCertificate(db.Model):
    __tablename__ = "competition_certificates"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz_attempts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("reading_competitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    position = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    pdf_path = db.Column(db.String(255), nullable=True)
    verification_code = db.Column(db.String(32), unique=True, nullable=False)
    issued_at = db.Column(db.DateTime, default=now_local, nullable=False)

    attempt = db.relationship("QuizAttempt", back_populates="certificate")
    user = db.relationship("User")
    competition = db.relationship("ReadingCompetition")

    @staticmethod
    def generate_code() -> str:
        return secrets.token_hex(8).upper()
