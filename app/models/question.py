from __future__ import annotations

from app import db
from app.utils.datetime import now_local
from app.models.category import QuestionCategory


class Question(db.Model):
    __tablename__ = "quiz_questions"

    TYPE_MULTIPLE_CHOICE = "multiple_choice"
    TYPE_TRUE_FALSE = "true_false"
    TYPE_SINGLE = "single_choice"
    TYPE_IMAGE = "image"
    TYPE_QUOTE = "quote"

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(30), nullable=False, default="single_choice")

    # ForeignKey to QuestionCategory
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("question_categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    image_path = db.Column(db.String(255), nullable=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id", ondelete="SET NULL"), nullable=True)
    explanation = db.Column(db.Text, nullable=True)
    points = db.Column(db.Integer, default=1, nullable=False)

    # Difficulty: easy, medium, hard
    difficulty = db.Column(db.String(20), default="medium", nullable=False)

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=now_local, nullable=False)
    updated_at = db.Column(db.DateTime, default=now_local, onupdate=now_local)

    # Relationships
    category = db.relationship("QuestionCategory", backref=db.backref("questions", lazy="dynamic"))
    book = db.relationship("Book")
    options = db.relationship(
        "QuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.sort_order",
    )

    def correct_option_ids(self) -> list[int]:
        return [opt.id for opt in self.options if opt.is_correct]

    def __repr__(self) -> str:
        return f"<Question {self.id} {self.question_text[:30]}...>"


class QuestionOption(db.Model):
    __tablename__ = "quiz_question_options"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    option_text = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    question = db.relationship("Question", back_populates="options")

    def __repr__(self) -> str:
        return f"<QuestionOption {self.id} (Correct: {self.is_correct})>"


class CompetitionQuestion(db.Model):
    __tablename__ = "competition_questions"
    __table_args__ = (
        db.UniqueConstraint(
            "competition_id",
            "question_id",
            name="uq_competition_question",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("reading_competitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    points_override = db.Column(db.Integer, nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    competition = db.relationship("ReadingCompetition", back_populates="competition_questions")
    question = db.relationship("Question")

    def __repr__(self) -> str:
        return f"<CompetitionQuestion Comp:{self.competition_id} Q:{self.question_id}>"
