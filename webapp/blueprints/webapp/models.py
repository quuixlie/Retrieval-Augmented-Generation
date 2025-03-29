from app import db


class Session(db.Model):
    __tablename__ = "sessions"

    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Session(ID={self.ID},name={self.name})"
