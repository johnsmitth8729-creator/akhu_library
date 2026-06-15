from app import db
from app.utils.datetime import now_local


class Faculty(db.Model):
    __tablename__ = "faculties"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=now_local,
        nullable=False
    )

    users = db.relationship(
        "User",
        back_populates="faculty_rel",
        foreign_keys="User.faculty_id",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Faculty {self.name}>"