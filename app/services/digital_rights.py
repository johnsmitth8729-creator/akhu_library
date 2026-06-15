"""Digital book access control helpers."""

from __future__ import annotations

import secrets

from flask import session
from flask_login import current_user

from app.models.system import Settings


def normalize_digital_access_flags(allow_download: bool, online_read_only: bool) -> tuple[bool, bool]:
    """Mutually exclusive: online read-only vs allow download."""
    if online_read_only:
        return False, True
    if allow_download:
        return True, False
    return bool(allow_download), bool(online_read_only)


def global_downloads_enabled() -> bool:
    setting = Settings.query.filter_by(key="allow_digital_downloads").first()
    if not setting:
        return True
    return setting.value.strip().lower() == "true"


def can_download_digital_book(book) -> bool:
    if book.online_read_only:
        return False
    if not book.allow_download:
        return False
    return global_downloads_enabled()


def issue_reader_access(user_id: int, book_id: int) -> str:
    token = secrets.token_urlsafe(32)
    session[f"reader_access_{book_id}"] = {
        "user_id": user_id,
        "token": token,
    }
    return token


def validate_reader_pdf_access(book_id: int, token: str | None) -> bool:
    if not current_user.is_authenticated:
        return False

    payload = session.get(f"reader_access_{book_id}")
    if not payload:
        return False

    return (
        payload.get("user_id") == current_user.id
        and payload.get("token") == token
        and bool(token)
    )
