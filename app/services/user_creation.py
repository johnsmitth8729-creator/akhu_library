from app import db
from app.models.faculty import Faculty
from app.models.user import User
from app.utils.phone import is_valid_phone, normalize_phone
from app.utils.username import generate_username
from app.services.user_import import default_temp_password


def assign_faculty(user: User, faculty_id: int | None) -> None:
    if not faculty_id:
        user.faculty_id = None
        user.faculty = None
        return

    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        raise ValueError("Faculty not found.")

    user.faculty_id = faculty.id
    user.faculty = faculty.name


def create_user_account(
    *,
    fullname: str,
    email: str,
    phone_number: str,
    faculty_id: int,
    group_name: str,
    password: str | None = None,
) -> tuple[User, str]:
    fullname = fullname.strip()
    group_name = group_name.strip()
    email = (email or "").strip().lower()

    if not fullname:
        raise ValueError("Full name is required.")

    if not email:
        raise ValueError("Email address is required.")

    if not group_name:
        raise ValueError("Group is required.")

    if not is_valid_phone(phone_number):
        raise ValueError("Enter a valid phone number.")

    normalized_phone = normalize_phone(phone_number)
    if User.query.filter_by(phone_number=normalized_phone).first():
        raise ValueError("Phone number already exists.")

    if User.query.filter_by(email=email).first():
        raise ValueError("Email already exists.")

    username = generate_username(fullname, phone_number)
    if User.query.filter_by(username=username).first():
        raise ValueError("Could not generate a unique username. Try a different phone number.")

    temp_password = password or default_temp_password()
    user = User(
        fullname=fullname,
        username=username,
        email=email,
        phone_number=normalized_phone,
        group_name=group_name,
        role=User.ROLE_USER,
        email_verified=False,
    )
    assign_faculty(user, faculty_id)
    user.set_password(temp_password)
    db.session.add(user)
    db.session.commit()
    return user, temp_password


create_student_user = create_user_account
