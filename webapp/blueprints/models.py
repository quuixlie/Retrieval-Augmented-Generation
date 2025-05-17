from __future__ import annotations

from sqlalchemy import inspect, event
from extensions import db


class ConfigModel(db.Model):
    """
    Configuration model attached to each message in conversation
    """
    __tablename__ = "configurations"

    """
    Application internal fields 
    If you add any new remember to exclude them in ConfigModel.get_values_dict()
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    """Default configuration is added when database is created and has id=0"""
    is_default = db.Column(db.Boolean, default=False, nullable=False)

    """
    Configuration options that will  be passed to the backend 
    """

    """Openrouter model id"""
    model_id = db.Column(db.String, nullable=False)
    """Name of the model"""
    model_name = db.Column(db.String, nullable=False)
    chunk_size = db.Column(db.Integer, nullable=False)

    @staticmethod
    def get_all() -> list[ConfigModel]:
        """
        Returns all configurations.
        The default configuration is always first
        :return: List of all configurations
        """
        return ConfigModel.query.order_by(ConfigModel.is_default.desc(), ConfigModel.id.desc()).all()

    @staticmethod
    def get_default() -> ConfigModel:
        """
        Returns default configuration
        :raises ValueError: If no default configuration is found (which shouldn't happen)
        :return: Default configuration
        """
        default = ConfigModel.query.filter_by(is_default=True).first()

        if not default:
            raise ValueError("No default configuration found in the database")

        return default

    @staticmethod
    def exists(config_id: int) -> bool:
        return ConfigModel.query.filter_by(id=config_id).first() is not None

    def get_values_dict(self) -> dict[str, any]:
        """
        Serialize to dictionary without application internal details (id, name,is_default)
        :return: Dictionary representation of the model
        """
        x = {c: getattr(self, c) for c in inspect(self).attrs.keys()}

        x.pop("id", None)
        x.pop("name", None)
        x.pop("is_default", None)

        return x


# Ensuring default configuration is not deleted
@event.listens_for(ConfigModel, "before_delete")
def prevent_default_config_deletion(_, __, target: ConfigModel):
    if target.is_default:
        raise Exception("Cannot delete default configuration")


class ConversationModel(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)

    messages = db.relationship("ChatMessageModel", cascade="all, delete-orphan")
    documents = db.relationship("DocumentModel", cascade="all, delete-orphan")

    """
    Current active configuration for the conversation
    If configuration is deleted it is set back to default configuration
    """
    active_config_id = db.Column(db.Integer,
                                 db.ForeignKey("configurations.id", ondelete="SET DEFAULT", onupdate="CASCADE"),
                                 server_default="0")
    active_config = db.relationship("ConfigModel")

    def __repr__(self):
        return f"Conversation(id={self.id}, title={self.title},active_config_id={self.active_config_i}"

    @staticmethod
    def exists(conversation_id: int) -> bool:
        """Returns true if conversation with given id exists"""
        return ConversationModel.query.filter_by(id=conversation_id).first() is not None


class ChatMessageModel(db.Model):
    __tablename__ = "chat_messages"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Chat messages are associated with a
    conversation_id = db.Column(db.Integer, db.ForeignKey(ConversationModel.id, ondelete="CASCADE", onupdate="CASCADE"))

    """User message, query"""
    message = db.Column(db.String)

    """Response from the LLM"""
    response = db.Column(db.String, nullable=True)

    """
    Configuration used to generate response for this message
    If configuration is deleted it is set to null
    """
    used_config_id = db.Column(db.Integer, db.ForeignKey(ConfigModel.id, ondelete="SET NULL", onupdate="CASCADE"),
                               nullable=True)
    used_config = db.relationship("ConfigModel")


class DocumentModel(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey(ConversationModel.id))

    """Original name of the file"""
    name = db.Column(db.String(64))
