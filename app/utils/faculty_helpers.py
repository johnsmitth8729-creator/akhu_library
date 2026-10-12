from app.models.faculty import Faculty


def get_faculty_choices(include_empty: bool = True) -> list[tuple[int, str]]:
    faculties = Faculty.query.order_by(Faculty.name.asc()).all()
    choices = [(faculty.id, faculty.name) for faculty in faculties]
    if include_empty:
        return [(0, "Select faculty")] + choices
    return choices


def load_faculty_choices(form, include_empty: bool = True) -> None:
    if hasattr(form, "faculty_id"):
        form.faculty_id.choices = get_faculty_choices(include_empty=include_empty)


def find_faculty_by_string(val: str | None) -> Faculty | None:
    if not val:
        return None
    val_clean = val.strip().lower()
    faculties = Faculty.query.all()
    # 1. Exact match
    for f in faculties:
        if f.name.strip().lower() == val_clean:
            return f

    # 2. Key/Alias match
    keywords = [
        ("software", "software engineering"),
        ("dastur", "software engineering"),
        ("dasturiy", "software engineering"),
        ("artificial", "artificial intelligence"),
        ("intellekt", "artificial intelligence"),
        ("sun", "artificial intelligence"),
        ("dron", "drone technologies"),
        ("drone", "drone technologies"),
        ("matemat", "applied mathematics"),
        ("amaliy", "applied mathematics"),
        ("kiber", "cybersecurity"),
        ("cyber", "cybersecurity"),
    ]
    for kw, target_faculty in keywords:
        if kw in val_clean:
            for f in faculties:
                if target_faculty in f.name.lower():
                    return f

    # 3. Substring match
    for f in faculties:
        if val_clean in f.name.lower() or f.name.lower() in val_clean:
            return f

    return None

