from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp, ValidationError


def _coerce_faculty_id(value):
    if value in (None, "", 0, "0"):
        return 0
    return int(value)

class RoleForm(FlaskForm):
    role = SelectField("Role", choices=[("user", "User"), ("librarian", "Librarian"), ("admin", "Admin")],
                       validators=[DataRequired()])
    submit = SubmitField("Update role")


class AdminUserForm(FlaskForm):
    fullname = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=2, max=120)]
    )
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=64),
            Regexp(
                r"^[A-Za-z0-9_]+$",
                message="Username can only contain letters, numbers and underscores."
            )
        ]
    )
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    phone_number = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Length(min=7, max=30),
            Regexp(r"^\+?[0-9\s().-]+$", message="Enter a valid phone number.")
        ]
    )
    faculty_id = SelectField(
        "Faculty",
        coerce=_coerce_faculty_id,
        validators=[Optional()],
        choices=[(0, "Select faculty")],
    )
    group_name = StringField(
        "Group",
        validators=[Optional(), Length(min=2, max=80)]
    )
    role = SelectField(
        "Role",
        choices=[
            ("user", "User"),
            ("librarian", "Librarian"),
            ("admin", "Admin")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Save User")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        if self.role.data == "user":
            is_valid = True

            if not self.faculty_id.data:
                self.faculty_id.errors.append("Faculty is required for user accounts.")
                is_valid = False

            if not (self.group_name.data or "").strip():
                self.group_name.errors.append("Group is required for user accounts.")
                is_valid = False

            return is_valid

        return True


class AdminCreateUserForm(AdminUserForm):
    password = PasswordField(
        "Temporary Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must contain at least 8 characters."),
            Regexp(
                r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$",
                message="Password must contain uppercase, lowercase and number."
            )
        ]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )


class AdminEditUserForm(AdminUserForm):
    password = PasswordField(
        "New Password",
        validators=[
            Optional(),
            Length(min=8, message="Password must contain at least 8 characters."),
            Regexp(
                r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$",
                message="Password must contain uppercase, lowercase and number."
            )
        ]
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[Optional()],
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        if self.password.data:
            if not self.confirm_password.data:
                self.confirm_password.errors.append("Please confirm the new password.")
                return False
            if self.password.data != self.confirm_password.data:
                self.confirm_password.errors.append("Passwords must match.")
                return False

        return True
