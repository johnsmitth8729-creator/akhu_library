import re


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    return digits


def is_valid_phone(phone: str) -> bool:
    digits = normalize_phone(phone)
    return 9 <= len(digits) <= 15


def phones_match(phone_a: str, phone_b: str) -> bool:
    return normalize_phone(phone_a) == normalize_phone(phone_b)
