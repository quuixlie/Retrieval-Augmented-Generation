from sqlalchemy.orm import backref

from app import db


class ConversationModel(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64))

    def __repr__(self):
        return f"Conversation(name={self.name})"


class ChatMessageModel(db.Model):
    __tablename__ = "chat_messages"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Chat messages are associated with a session
    conversation_id = db.Column(db.Integer, db.ForeignKey(ConversationModel.id, ondelete="CASCADE", onupdate="CASCADE"))
    message = db.Column(db.String(2048))
    # Each message in the chat should have a response
    response = db.Column(db.String(4096), nullable=True)
