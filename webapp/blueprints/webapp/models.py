from sqlalchemy.orm import backref

from app import db


class ConversationModel(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64))

    """
    Current active configuration for the conversation
    If configuration is deleted it is set to null
    """

    active_config_id = db.Column(db.Integer,
                                 db.ForeignKey("configurations.id", ondelete="SET NULL", onupdate="CASCADE"),
                                 nullable=True)

    def __repr__(self):
        return f"Conversation(id={self.id}, title={self.title},active_config_id={self.active_config_i}"

    @staticmethod
    def exists(id: int) -> bool:
        return ConversationModel.query.filter_by(id=id).first() is not None


class ChatMessageModel(db.Model):
    __tablename__ = "chat_messages"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Chat messages are associated with a session
    conversation_id = db.Column(db.Integer, db.ForeignKey(ConversationModel.id, ondelete="CASCADE", onupdate="CASCADE"))
    message = db.Column(db.String(2048))
    # Each message in the chat should have a response
    response = db.Column(db.String(4096), nullable=True)

    """
    Configuration used to generate response for this message
    If configuration is deleted it is set to null
    """
    used_config_id = db.Column(db.Integer,
                               db.ForeignKey("configurations.id", ondelete="SET NULL", onupdate="CASCADE"),
                               nullable=True)


class DocumentModel(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey(ConversationModel.id, ondelete="CASCADE", onupdate="CASCADE"))

    """Original name of the file"""
    name = db.Column(db.String(64))

    """Name of the file that is stored on the server"""
    path = db.Column(db.String(256))

    @staticmethod
    def exists_with_path(path: str) -> bool:
        return DocumentModel.query.filter_by(path=path).first() is not None


class ConfigModel(db.Model):
    """
    Configuration model attached to each message in conversation
    """
    __tablename__ = "configurations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_name = db.Column(db.String(64), nullable=False)
