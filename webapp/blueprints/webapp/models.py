from __future__ import annotations
from sqlalchemy import inspect, event
from app import db


class ConfigModel(db.Model):
    """
    Configuration model attached to each message in conversation

    """
    __tablename__ = "configurations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)

    """Default configuration is added when database is created and has id=0"""
    is_default = db.Column(db.Boolean, default=False, nullable=False)

    """Openrouter model id"""
    model_id = db.Column(db.String(64), nullable=False)
    """Name of the model"""
    model_name = db.Column(db.String(64), nullable=False)
    chunk_size = db.Column(db.Integer, nullable=False)
    document_count = db.Column(db.Integer, nullable=False)
    """
    Add more configuration options here
    And in get_default() if necessary
    """

    @staticmethod
    def get_all() -> list[ConfigModel]:
        """
        Returns all configurations.
        The default configuration is always first
        :return: List of all configurations
        """
        return ConfigModel.query.all().sort(ConfigModel.is_default.desc())

    @staticmethod
    def get_default() -> ConfigModel:
        """
        Returns default configuration
        :return: Default configuration
        """
        default = ConfigModel.query.filter_by(is_default=True).first()

        print("DEF: ", default)

        if not default:
            raise ValueError("No default configuration found in the database")

        return default

    @staticmethod
    def exists(id: int) -> bool:
        return ConfigModel.query.filter_by(id=id).first() is not None

    def get_values_dict(self) -> dict[str, any]:
        """
        Serialize to dictionary without application internal details (id, name)
        :return: Dictionary representation of the model
        """
        x = {c: getattr(self, c) for c in inspect(self).attrs.keys()}

        x.pop("id", None)
        x.pop("name", None)
        x.pop("is_default", None)

        return x


# Ensuring default configuration is not deleted
@event.listens_for(ConfigModel, "before_delete")
def prevent_default_config_deletion(mapper, connection, target: ConfigModel):
    if target.is_default:
        raise Exception("Cannot delete default configuration")


# @event.listens_for(ConfigModel, "after_delete")
# def set_default_config(mapper, connection, target: ConfigModel):
#    """
#    Ensures Conversations and chat messages do not point to deleted configuration
#
#    This was done because of (potential skill issue) i couldn't get ON DELETE SET DEFAULT behaviour to work
#    """
#
#    connection.execute(
#        ConversationModel.__table__.update().where(ConversationModel.active_config_id == target.id).values(
#            active_config_id=0))
#
#    connection.execute(
#        ChatMessageModel.__table__.update().where(ChatMessageModel.used_config_id == target.id).values(
#            used_config_id=0))


class ConversationModel(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64))

    messages = db.relationship("ChatMessageModel", cascade="all, delete-orphan")
    documents = db.relationship("DocumentModel", cascade="all, delete-orphan")

    """
    Current active configuration for the conversation
    If configuration is deleted it is set to null
    """
    active_config_id = db.Column(db.Integer,
                                 db.ForeignKey("configurations.id", ondelete="SET DEFAULT", onupdate="CASCADE"),
                                 server_default="0")
    active_config = db.relationship("ConfigModel")

    def __repr__(self):
        return f"Conversation(id={self.id}, title={self.title},active_config_id={self.active_config_i}"

    @staticmethod
    def exists(id: int) -> bool:
        """Returns true if conversation with given id exists"""
        return ConversationModel.query.filter_by(id=id).first() is not None


class ChatMessageModel(db.Model):
    __tablename__ = "chat_messages"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Chat messages are associated with a
    conversation_id = db.Column(db.Integer, db.ForeignKey(ConversationModel.id))

    """User message, query"""
    message = db.Column(db.String(2048))

    """Response from the LLM"""
    response = db.Column(db.String(4096), nullable=True)

    """
    Configuration used to generate response for this message
    If configuration is deleted it is set to null
    """
    used_config_id = db.Column(db.Integer, db.ForeignKey(ConfigModel.id))
    used_config = db.relationship("ConfigModel")


class DocumentModel(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey(ConversationModel.id))

    """Original name of the file"""
    name = db.Column(db.String(64))

    """Name of the file that is stored on the server (within the upload folder)"""
    path = db.Column(db.String(256))

    @staticmethod
    def exists_with_path(path: str) -> bool:
        """Returns true if document with given path (within the upload folder) exists"""
        return DocumentModel.query.filter_by(path=path).first() is not None
