from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Regexp,
    Optional,
)


# =====================================================
# REGISTER FORM
# =====================================================

class RegisterForm(FlaskForm):

    fullname = StringField(

        "Full Name",

        validators=[

            DataRequired(),

            Length(
                min=2,
                max=120
            )
        ]
    )


    username = StringField(

        "Username",

        validators=[

            DataRequired(),

            Length(
                min=3,
                max=64
            ),

            Regexp(

                r"^[A-Za-z0-9_]+$",

                message=
                "Username can only contain "
                "letters, numbers and underscores."
            )
        ]
    )


    email = StringField(

        "Email Address",

        validators=[

            DataRequired(),

            Email(),

            Length(max=120)
        ]
    )

    phone_number = StringField(

        "Phone Number",

        validators=[

            DataRequired(),

            Length(
                min=7,
                max=30
            ),

            Regexp(

                r"^\+?[0-9\s().-]+$",

                message="Enter a valid phone number."
            )
        ]
    )

    faculty_id = SelectField(

        "Faculty",

        coerce=int,

        validators=[

            DataRequired()
        ]
    )


    group_name = StringField(

        "Group",

        validators=[

            DataRequired(),

            Length(
                min=2,
                max=80
            )
        ]
    )


    password = PasswordField(

        "Password",

        validators=[

            DataRequired(),

            Length(
                min=8,
                message=
                "Password must contain "
                "at least 8 characters."
            ),

            Regexp(

                r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$",

                message=
                "Password must contain "
                "uppercase, lowercase and number."
            )
        ]
    )


    confirm = PasswordField(

        "Confirm Password",

        validators=[

            DataRequired(),

            EqualTo(
                "password",
                message="Passwords must match."
            )
        ]
    )


    submit = SubmitField(
        "Create Account"
    )


# =====================================================
# LOGIN FORM
# =====================================================

class LoginForm(FlaskForm):

    email = StringField(

        "Email or Username",

        validators=[
            DataRequired()
        ]
    )


    password = PasswordField(

        "Password",

        validators=[
            DataRequired()
        ]
    )


    submit = SubmitField(
        "Sign In"
    )


# =====================================================
# FORGOT PASSWORD FORM
# =====================================================

class ForgotPasswordForm(FlaskForm):

    email = StringField(

        "Email Address",

        validators=[

            DataRequired(),

            Email()
        ]
    )


    submit = SubmitField(
        "Send Reset Link"
    )


# =====================================================
# RESET PASSWORD FORM
# =====================================================

class ResetPasswordForm(FlaskForm):

    password = PasswordField(

        "New Password",

        validators=[

            DataRequired(),

            Length(
                min=8
            ),

            Regexp(

                r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$",

                message=
                "Password must contain uppercase, lowercase and number."
            )
        ]
    )


    confirm_password = PasswordField(

        "Confirm New Password",

        validators=[

            DataRequired(),

            EqualTo(
                "password",
                message="Passwords must match."
            )
        ]
    )


    submit = SubmitField(
        "Reset Password"
    )

# =====================================================
# PROFILE UPDATE FORM
# =====================================================

class ProfileUpdateForm(FlaskForm):
    fullname = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=2, max=120)]
    )

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=64),
            Regexp(r"^[A-Za-z0-9_]+$", message="Username can only contain letters, numbers and underscores.")
        ]
    )

    faculty_id = SelectField(
        "Faculty",
        coerce=int,
        validators=[Optional()],
        choices=[(0, "Select faculty")],
    )

    group_name = StringField(
        "Group",
        validators=[Length(max=80)]
    )

    phone_number = StringField(
        "Phone Number",
        validators=[
            Length(max=30),
            Regexp(r"^\+?[0-9\s().-]*$", message="Enter a valid phone number.")
        ]
    )

    avatar = FileField(
        "Profile Picture",
        validators=[FileAllowed(["jpg", "png", "jpeg", "webp"], "Images only!")]
    )

    submit = SubmitField("Update Profile")
