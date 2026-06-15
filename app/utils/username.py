import re
import unicodedata

from app.models.user import User


UZBEK_REPLACEMENTS = (
    ("o'", "o"),
    ("g'", "g"),
    ("oʻ", "o"),
    ("o‘", "o"),
    ("gʻ", "g"),
    ("g‘", "g"),
    ("sh", "sh"),
    ("ch", "ch"),
    ("ng", "ng"),
    ("ä", "a"),
    ("ö", "o"),
    ("ü", "u"),
    ("ə", "e"),
    ("ç", "c"),
    ("ş", "s"),
    ("ğ", "g"),
    ("ı", "i"),
    ("’", ""),
    ("'", ""),
)


def transliterate_text(value: str) -> str:
    text = (value or "").strip().lower()
    for old, new in UZBEK_REPLACEMENTS:
        text = text.replace(old, new)

    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return re.sub(r"[^a-z0-9]", "", ascii_text)


def split_fullname(fullname: str) -> tuple[str, str]:
    parts = [part for part in re.split(r"\s+", (fullname or "").strip()) if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts[0], parts[-1]


def phone_suffix(phone: str, length: int = 2) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) < length:
        return digits
    return digits[-length:]


def build_username_base(fullname: str, phone: str) -> str:
    first, last = split_fullname(fullname)
    first_slug = transliterate_text(first)
    last_slug = transliterate_text(last)
    suffix = phone_suffix(phone)
    base = f"{first_slug}{last_slug}{suffix}"
    return base[:58] if base else "user"


def ensure_unique_username(base: str) -> str:
    base = (base or "user")[:58]
    if not User.query.filter_by(username=base).first():
        return base

    counter = 1
    while counter < 10000:
        suffix = f"_{counter}"
        candidate = f"{base[: 64 - len(suffix)]}{suffix}"
        if not User.query.filter_by(username=candidate).first():
            return candidate
        counter += 1

    raise ValueError("Unable to generate a unique username.")


def generate_username(fullname: str, phone: str) -> str:
    return ensure_unique_username(build_username_base(fullname, phone))


def reserve_username(base: str, reserved: set[str]) -> str:
    """Reserve a username within a batch import (in-memory set)."""
    base = (base or "user")[:58]
    if base not in reserved and not User.query.filter_by(username=base).first():
        reserved.add(base)
        return base

    counter = 1
    while counter < 10000:
        suffix = f"_{counter}"
        candidate = f"{base[: 64 - len(suffix)]}{suffix}"
        if candidate not in reserved and not User.query.filter_by(username=candidate).first():
            reserved.add(candidate)
            return candidate
        counter += 1

    raise ValueError("Unable to generate a unique username.")
