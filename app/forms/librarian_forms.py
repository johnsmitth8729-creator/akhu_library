from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, SelectField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email, Regexp

class CategoryForm(FlaskForm):
    name = StringField("Category name", validators=[DataRequired(), Length(1, 80)])
    submit = SubmitField("Save")

class AuthorForm(FlaskForm):
    fullname = StringField("Author name", validators=[DataRequired(), Length(1, 120)])
    submit = SubmitField("Save")

class BorrowForm(FlaskForm):
    user_id = SelectField("User", coerce=int, validators=[DataRequired()])
    book_id = SelectField("Book", coerce=int, validators=[DataRequired()])
    days = IntegerField("Days", validators=[DataRequired(), NumberRange(min=1, max=120)], default=14)
    submit = SubmitField("Lend book")


class ManualUserForm(FlaskForm):
    fullname = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=2, max=120)],
    )
    email = EmailField(
        "Email Address",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    phone_number = StringField(
        "Phone Number",
        validators=[
            DataRequired(),
            Length(min=9, max=30),
            Regexp(r"^\+?[0-9\s().-]+$", message="Enter a valid phone number."),
        ],
    )
    faculty_id = SelectField("Faculty", coerce=int, validators=[DataRequired()])
    group_name = StringField(
        "Group",
        validators=[DataRequired(), Length(min=2, max=80)],
    )
    submit = SubmitField("Create User")


# Backward-compatible alias
ManualStudentForm = ManualUserForm


class UserImportForm(FlaskForm):
    faculty_id = SelectField("Faculty", coerce=int, validators=[DataRequired()])
    excel_file = FileField(
        "Excel file",
        validators=[
            DataRequired(),
            FileAllowed(["xlsx", "xls"], "Only .xlsx and .xls files are allowed."),
        ],
    )
    default_password = StringField(
        "Default Password",
        validators=[Optional(), Length(min=6, max=80)],
    )
    submit = SubmitField("Upload and Preview")
