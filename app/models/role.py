from app import db

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship("User", backref="role_relation", lazy="dynamic")

    def __repr__(self):
        return f"<Role {self.name}>"
