import requests
from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from app import db
from appconfig import AppConfig
from .models import ChatMessageModel, ConversationModel, DocumentModel, ConfigModel

chat_bp = Blueprint("chat", __name__)


@chat_bp.route('/<int:conversation_id>', methods=["GET"])
def index(conversation_id: int):
    conversation = ConversationModel.query.filter(ConversationModel.id == conversation_id).first()

    if not conversation:
        return redirect(url_for('webapp.chat.new'))

    messages = ChatMessageModel.query.filter(ChatMessageModel.conversation_id == conversation_id).all()

    attached_documents = DocumentModel.query.filter(DocumentModel.conversation_id == conversation_id).all()

    return render_template('chat.html', messages=messages, attached_documents=attached_documents,
                           conversation_id=conversation_id)


@chat_bp.route('/new', methods=['GET'])
def new():
    """Optional config """
    config_id = request.args.get("config_id", type=int)

    if config_id and not ConfigModel.exists(config_id):
        config_id = None

    # Default config
    if not config_id:
        config_id = ConfigModel.get_default().id

    config_name = ConfigModel.query.get(config_id).name
    new_conversation = ConversationModel(title=f"Conversation with {config_name}", active_config_id=config_id)
    db.session.add(new_conversation)
    db.session.commit()

    print("Created conversation with id: ", new_conversation.id)

    return redirect(url_for('webapp.chat.index', conversation_id=new_conversation.id))


@chat_bp.route('/delete/<int:id>', methods=["DELETE"])
def delete(id: int):
    if not id:
        print("No del_id provided")
        return "", 400

    if not ConversationModel.exists(id):
        print(f"Conversation {id} does not exist - cannot delete it")

        return "", 400

    db.session.delete(ConversationModel.query.filter(ConversationModel.id == id).first())
    db.session.commit()

    print(ConversationModel.query.filter(ConversationModel.id == id).first())

    return "", 200


@chat_bp.route('/send/<int:conversation_id>', methods=["POST"])
def send(conversation_id: int):
    conversation = ConversationModel.query.filter(ConversationModel.id == conversation_id).first()

    if not conversation:
        return jsonify({"error": "Invalid conversation"}), 400

    message = request.form.get("message", None)

    if not message:
        return jsonify({"error": "Message not provided"}), 400

    url = AppConfig.API_BASE_URL + url_for("api.index", conversation_id=conversation_id)

    config_dict = conversation.active_config.get_values_dict()

    response = requests.post(url, json={"query": message, "config": config_dict})

    try:
        responseJSON = response.json()

        if responseJSON.get("error", None):
            return jsonify({"error": responseJSON.get("error")}), 400

        response_message = responseJSON.get("message", None)
        # Saving to the db
        new_message = ChatMessageModel(conversation_id=conversation_id, message=message, response=response_message)
        db.session.add(new_message)
        db.session.commit()

        return jsonify({"rag_response": response_message})

    except Exception as e:
        print(e)
        return jsonify({"error": "Unknown error occurred"}), 500
