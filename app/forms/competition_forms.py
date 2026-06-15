from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SelectMultipleField,
    SubmitField,
    SelectField,
    FileField,
    BooleanField,
)

from wtforms.validators import (
    DataRequired,
    Optional,
    Length,
    NumberRange,
)


class CompetitionForm(FlaskForm):
    title = StringField(
        "Competition Title",
        validators=[
            DataRequired(),
            Length(max=200),
        ],
    )

    competition_type = SelectField(
        "Competition Scope",
        choices=[
            ("university", "All students"),
            ("faculty", "Selected faculties"),
        ],
        validators=[DataRequired()],
        default="university",
    )

    visibility = SelectField(
        "Visibility",
        choices=[("public", "Public")],
        validators=[DataRequired()],
        default="public",
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=3000),
        ],
    )

    start_date = StringField(
        "Start Date",
        validators=[
            DataRequired()
        ],
    )

    end_date = StringField(
        "End Date",
        validators=[
            DataRequired()
        ],
    )

    competition_image = FileField("Competition Image", validators=[Optional()])

    book_ids = SelectMultipleField("Books", coerce=int, validators=[Optional()])

    faculty_ids = SelectMultipleField(
        "Faculties",
        coerce=int,
        validators=[Optional()],
    )

    group_names = StringField("Group Names", validators=[Optional(), Length(max=400)])
    question_ids = SelectMultipleField("Questions", coerce=int, validators=[Optional()])

    max_attempts = IntegerField(
        "Maximum Attempts",
        default=1,
        validators=[
            NumberRange(min=1, max=20),
        ],
    )

    passing_score = IntegerField(
        "Passing Score (%)",
        default=60,
        validators=[
            NumberRange(min=0, max=100),
        ],
    )

    top_winners_count = IntegerField(
        "Number of Winners",
        default=3,
        validators=[
            NumberRange(min=1, max=20),
        ],
    )

    time_limit_minutes = IntegerField(
        "Time Limit (Minutes)",
        validators=[
            Optional(),
            NumberRange(min=1, max=300),
        ],
    )

    # Used by app/routes/competitions.py + manage/form.html
    randomize_questions = BooleanField("Randomize Questions", default=True)
    randomize_answers = BooleanField("Randomize Answers", default=True)
    prevent_reopen_completed = BooleanField(
        "Prevent Reopen Completed",
        default=True,
    )

    secure_quiz_mode = BooleanField("Secure Quiz Mode", default=True)
    enable_watermark = BooleanField("Enable Watermark", default=True)
    disable_copy = BooleanField("Disable Copy", default=True)
    disable_print = BooleanField("Disable Print", default=True)
    require_fullscreen = BooleanField("Require Fullscreen", default=False)
    track_focus_loss = BooleanField("Track Focus Loss", default=True)
    track_devtools = BooleanField("Track DevTools", default=True)

    submit = SubmitField("Save Competition")


class QuestionForm(FlaskForm):
    """Question bank create/edit form."""

    question_text = TextAreaField(
        "Question Text",
        validators=[
            DataRequired(),
            Length(max=5000),
        ],
    )

    question_type = SelectField(
        "Question Type",
        choices=[
            ("single_choice", "Single Choice"),
            ("multiple_choice", "Multiple Choice"),
            ("true_false", "True/False"),
            ("image", "Image Question"),
            ("quote", "Quote Question"),
        ],
        validators=[DataRequired()],
        default="single_choice"
    )

    category_id = SelectField(
        "Question Category",
        coerce=int,
        choices=[],
        validators=[Optional()]
    )

    difficulty = SelectField(
        "Difficulty Level",
        choices=[
            ("easy", "Easy"),
            ("medium", "Medium"),
            ("hard", "Hard"),
        ],
        validators=[DataRequired()],
        default="medium"
    )

    points = IntegerField(
        "Points",
        default=1,
        validators=[
            DataRequired(),
            NumberRange(min=1, max=1000),
        ],
    )

    explanation = TextAreaField(
        "Explanation / Solution Key",
        validators=[Optional(), Length(max=3000)],
    )

    # choices populated dynamically by router
    book_id = SelectField(
        "Book Reference",
        choices=[(0, "— None —")],
        coerce=int,
        validators=[Optional()],
    )

    # Optional image upload
    image_file = FileField(
        "Question Image Asset",
        validators=[Optional()]
    )

    submit = SubmitField("Save Question")


class QuestionCategoryForm(FlaskForm):
    """Question Category creation/editing form."""

    name = StringField(
        "Category Name",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    submit = SubmitField("Save Category")


def parse_datetime_local(value: str) -> datetime:
    value = (value or "").strip()

    for fmt in (
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    raise ValueError("Invalid date format.")
