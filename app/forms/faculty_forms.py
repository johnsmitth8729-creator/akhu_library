from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class FacultyForm(FlaskForm):
    name = StringField(
        "Faculty name",
        validators=[DataRequired(), Length(min=2, max=120)],
    )
    submit = SubmitField("Save")
