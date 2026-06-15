from app.models.user import User


def resolve_user_email(email: str | None, username: str) -> str:
    if email and email.strip():
        return email.strip().lower()

    base = (username or "user")[:50].lower()
    candidate = f"{base}@students.akhu.uz"
    counter = 1

    while User.query.filter_by(email=candidate).first():
        candidate = f"{base}{counter}@students.akhu.uz"
        counter += 1

    return candidate
