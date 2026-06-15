from urllib.parse import urljoin, urlsplit

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.system import Settings
from app.forms.auth_forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from app.utils.helpers import log_activity
from app.utils.faculty_helpers import load_faculty_choices
from app.services.user_creation import assign_faculty
from app.utils.phone import normalize_phone, is_valid_phone
from flask_mail import Message
from app import mail

auth_bp = Blueprint("auth", __name__)


def is_safe_redirect_url(target):
    if not target:
        return False

    host_url = urlsplit(request.host_url)
    redirect_url = urlsplit(urljoin(request.host_url, target))

    return (
        redirect_url.scheme in ("http", "https")
        and redirect_url.netloc == host_url.netloc
    )

# =====================================================
# SEND RESET EMAIL
# =====================================================

def send_reset_email(user):

    token = user.generate_reset_token()

    reset_url = url_for(

        "auth.reset_password",

        token=token,

        _external=True
    )

    msg = Message(

        subject=
        "Password Reset | Al-Khwarizmi Smart Library",

        recipients=[user.email]
    )

    msg.html = f"""

    <div style="
        font-family:Arial;
        padding:40px;
        background:#f8fafc;
    ">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            border-radius:20px;
            padding:40px;
        ">

            <h1 style="color:#0f172a;">
                Password Reset
            </h1>

            <p style="
                color:#475569;
                line-height:1.8;
            ">

                Hello {user.fullname},

                You requested a password reset for your
                Smart Library account.

            </p>

            <div style="margin:40px 0;">

                <a
                    href="{reset_url}"
                    style="
                        background:#2563eb;
                        color:white;
                        padding:16px 28px;
                        text-decoration:none;
                        border-radius:12px;
                        font-weight:700;
                    "
                >

                    Reset Password

                </a>

            </div>

            <p style="
                color:#64748b;
                font-size:14px;
            ">

                This link expires in 30 minutes.

            </p>

        </div>

    </div>

    """

    mail.send(msg)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    allow_registration = Settings.query.filter_by(
        key="allow_registration"
    ).first()

    if (
        allow_registration
        and allow_registration.value.lower() != "true"
    ):
        flash("Public registration is currently disabled.", "warning")
        return redirect(url_for("auth.login"))

    form = RegisterForm()
    load_faculty_choices(form, include_empty=True)

    if not form.faculty_id.choices or form.faculty_id.choices == [(0, "Select faculty")]:
        flash("Registration is unavailable until faculties are configured.", "warning")
        return redirect(url_for("auth.login"))

    if form.validate_on_submit():
        if form.faculty_id.data == 0:
            form.faculty_id.errors.append("Please select a faculty.")
            return render_template("auth/register.html", form=form)

        if not is_valid_phone(form.phone_number.data):
            flash("Enter a valid phone number.", "danger")
            return render_template("auth/register.html", form=form)

        normalized_phone = normalize_phone(form.phone_number.data)
        if User.query.filter_by(phone_number=normalized_phone).first():
            flash("Phone number already in use.", "danger")
            return render_template("auth/register.html", form=form)

        if User.query.filter((User.email == form.email.data) | (User.username == form.username.data)).first():
            flash("Email or username already in use.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(
            fullname=form.fullname.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            phone_number=normalized_phone,
            group_name=form.group_name.data.strip(),
            role=User.ROLE_USER,
        )
        try:
            assign_faculty(user, form.faculty_id.data)
        except ValueError:
            flash("Selected faculty is invalid.", "danger")
            return render_template("auth/register.html", form=form)

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        log_activity(user.id, "Registered new account")
        
        try:
            from app.utils.telegram import send_telegram_notification
            send_telegram_notification(
                f"🆕 <b>Yangi foydalanuvchi ro'yxatdan o'tdi:</b>\n"
                f"Foydalanuvchi: {user.fullname}\n"
                f"Email: {user.email}\n"
                f"Username: @{user.username}"
            )
        except Exception:
            pass

        flash("Welcome! Your account is ready.", "success")
        login_user(user)
        return redirect(url_for("main.home"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.email.data.strip().lower()
        user = User.query.filter(
            (User.email == identifier) | (User.username == form.email.data.strip())
        ).first()
        if user and user.check_password(form.password.data):
            if user.is_blocked:

                flash(
                    "Your account has been blocked.",
                    "danger"
                )

                return render_template(
                    "auth/login.html",
                    form=form
                )

            login_user(user, remember=True)
            user.update_last_login()
            log_activity(user.id, "Logged in")
            flash(f"Welcome back, {user.fullname}!", "success")
            next_url = request.args.get("next")
            if is_safe_redirect_url(next_url):
                return redirect(next_url)
            return redirect(url_for("main.home"))
        flash("Invalid credentials.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    log_activity(current_user.id, "Logged out")
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.home"))

# =====================================================
# FORGOT PASSWORD
# =====================================================

@auth_bp.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if current_user.is_authenticated:

        return redirect(
            url_for("main.home")
        )

    form = ForgotPasswordForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data.lower()
        ).first()

        if user:

            send_reset_email(user)

        flash(

            "If an account exists with this email, "
            "a reset link has been sent.",

            "info"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(

        "auth/forgot_password.html",

        form=form
    )


# =====================================================
# RESET PASSWORD
# =====================================================

@auth_bp.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password(token):

    if current_user.is_authenticated:

        return redirect(
            url_for("main.home")
        )

    user = User.verify_reset_token(token)

    if not user:

        flash(
            "Invalid or expired reset token.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    form = ResetPasswordForm()

    if form.validate_on_submit():

        user.set_password(
            form.password.data
        )

        db.session.commit()

        flash(
            "Your password has been updated successfully.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(

        "auth/reset_password.html",

        form=form,
        title="Reset Password"
    )


@auth_bp.route(
    "/change-password",
    methods=["GET", "POST"]
)
@login_required
def change_password():
    form = ResetPasswordForm()

    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        log_activity(current_user.id, "Changed password")

        flash(
            "Your password has been changed successfully.",
            "success"
        )

        return redirect(
            url_for("user.profile")
        )

    return render_template(
        "auth/reset_password.html",
        form=form,
        title="Change Password"
    )
