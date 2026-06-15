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
