from app import db
from app.utils.datetime import now_local


class QuestionCategory(db.Model):
    __tablename__ = "question_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=now_local, nullable=False)

    def __repr__(self) -> str:
        return f"<QuestionCategory {self.name}>"
