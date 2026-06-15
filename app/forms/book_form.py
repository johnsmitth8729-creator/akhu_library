from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SelectField,
    SubmitField,
    BooleanField
)

from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    NumberRange,
    ValidationError
)
from werkzeug.datastructures import FileStorage


def _read_file_header(file_storage, size=16):
    stream = file_storage.stream

    try:
        position = stream.tell()
    except (AttributeError, OSError):
        position = None

    header = stream.read(size)

    if position is not None:
        stream.seek(position)
    else:
        stream.seek(0)

    return header


def _matches_file_signature(ext, header):
    signatures = {
        "pdf": lambda value: value.startswith(b"%PDF-"),
        "jpg": lambda value: value.startswith(b"\xff\xd8\xff"),
        "jpeg": lambda value: value.startswith(b"\xff\xd8\xff"),
        "png": lambda value: value.startswith(b"\x89PNG\r\n\x1a\n"),
        "webp": lambda value: value.startswith(b"RIFF") and value[8:12] == b"WEBP",
    }

    matcher = signatures.get(ext)
    return matcher is None or matcher(header)


class FileAllowed(object):

    def __init__(self, upload_set, message=None):
        self.upload_set = [ext.lower() for ext in upload_set]
        self.message = message

    def __call__(self, form, field):

        # No file selected
        if field.data is None:
            return

        # Browser empty upload
        if isinstance(field.data, FileStorage):

            if field.data.filename == "":
                return

            filename = field.data.filename.lower()

            if "." not in filename:
                raise ValidationError(
                    self.message or "Invalid file."
                )

            ext = filename.rsplit(".", 1)[1]

            if ext not in self.upload_set:
                raise ValidationError(
                    self.message or
                    f"Only {', '.join(self.upload_set)} files are allowed."
                )

            header = _read_file_header(field.data)

            if not _matches_file_signature(ext, header):
                raise ValidationError(
                    self.message or "Uploaded file content does not match its extension."
                )


# =====================================================
# BASE BOOK FORM
# =====================================================

class BaseBookForm(FlaskForm):

    # =========================
    # BASIC
    # =========================

    title = StringField(
        "Book Title",
        validators=[
            DataRequired(),
            Length(max=200)
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=4000)
        ]
    )

    isbn = StringField(
        "ISBN",
        validators=[
            Optional(),
            Length(max=30)
        ]
    )

    language = StringField(
        "Language",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    published_year = IntegerField(
        "Published Year",
        validators=[
            Optional(),
            NumberRange(min=1000, max=2100)
        ]
    )

    # =========================
    # AUTHOR
    # =========================

    author_id = SelectField(
        "Author",
        coerce=int,
        validators=[Optional()]
    )

    use_new_author = BooleanField(
        "Add New Author"
    )

    new_author = StringField(
        "New Author",
        validators=[
            Optional(),
            Length(max=120)
        ]
    )

    # =========================
    # CATEGORY
    # =========================

    category_id = SelectField(
        "Category",
        coerce=int,
        validators=[Optional()]
    )

    use_new_category = BooleanField(
        "Add New Category"
    )

    new_category = StringField(
        "New Category",
        validators=[
            Optional(),
            Length(max=120)
        ]
    )

    # =========================
    # COVER
    # =========================

    cover_image = FileField(
        "Cover Image",
        validators=[
            Optional(),
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Only image files allowed."
            )
        ]
    )



# =====================================================
# PHYSICAL BOOK FORM
# =====================================================

class PhysicalBookForm(BaseBookForm):

    nn_numbers = TextAreaField(
        "NN Numbers (one per line)",
        validators=[
            DataRequired(),
            Length(max=4000)
        ]
    )

    library_location = StringField(
        "Library Location",
        validators=[
            Optional(),
            Length(max=120)
        ]
    )

    shelf_code = StringField(
        "Shelf Code",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    submit = SubmitField(
        "Save Physical Book"
    )



# =====================================================
# DIGITAL BOOK FORM
# =====================================================

class DigitalBookForm(BaseBookForm):

    pdf_file = FileField(
        "PDF File",
        validators=[
            DataRequired(),
            FileAllowed(
                ["pdf"],
                "PDF files only."
            )
        ]
    )

    allow_download = BooleanField(
        "Allow Download"
    )

    online_read_only = BooleanField(
        "Online Read Only",
        default=False
    )

    submit = SubmitField(
        "Save Digital Book"
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        if self.allow_download.data and self.online_read_only.data:
            self.online_read_only.errors.append(
                "Online Read Only and Allow Download cannot both be enabled."
            )
            return False

        return True
