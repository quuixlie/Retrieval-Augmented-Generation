from app import db


class SessionModel(db.Model):
    __tablename__ = "sessions"

    name = db.Column(db.String(50), primary_key=True)

    def __repr__(self):
        return f"Session(name={self.name})"
