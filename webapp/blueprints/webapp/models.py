from sqlalchemy.orm import backref

from app import db


class SessionModel(db.Model):
    __tablename__ = "sessions"

    name = db.Column(db.String(50), primary_key=True)

    def __repr__(self):
        return f"Session(name={self.name})"


class ChatMessageModel(db.Model):
    __tablename__ = "chat_messages"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Chat messages are associated with a session
    session_name = db.Column(db.String(50), db.ForeignKey(SessionModel.name, ondelete="CASCADE", onupdate="CASCADE"))
    message = db.Column(db.String(512))
    # Each message in the chat should have a response
    response = db.Column(db.String(512), nullable=True)
