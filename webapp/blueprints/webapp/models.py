from sqlalchemy.orm import backref

from app import db


class ConversationModel(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64))

    def __repr__(self):
        return f"Conversation(name={self.name})"

    @staticmethod
    def exists(id: int) -> bool:
        return ConversationModel.query.filter_by(id=id).first() is not None


class DocumentModel(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey(ConversationModel.id, ondelete="CASCADE", onupdate="CASCADE"))
    name = db.Column(db.String(64))

    @staticmethod
    def exists_with_name(name: str) -> bool:
        return DocumentModel.query.filter_by(name=name).first() is not None


class ChatMessageModel(db.Model):
    __tablename__ = "chat_messages"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Chat messages are associated with a session
    conversation_id = db.Column(db.Integer, db.ForeignKey(ConversationModel.id, ondelete="CASCADE", onupdate="CASCADE"))
    message = db.Column(db.String(2048))
    # Each message in the chat should have a response
    response = db.Column(db.String(4096), nullable=True)
