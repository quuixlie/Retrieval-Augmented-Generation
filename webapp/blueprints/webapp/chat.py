import time

import requests
from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from app import db
from config import Config
from .models import ChatMessageModel, ConversationModel, DocumentModel

chat_bp = Blueprint("chat", __name__)


@chat_bp.route('/<int:conversation_id>', methods=["GET"])
def index(conversation_id: int):
    conversation = ConversationModel.query.filter(ConversationModel.id == conversation_id).first()

    if not conversation:
        return redirect(url_for('webapp.sessions.index', success=False, msg="Conversation does not exist"))

    messages = ChatMessageModel.query.filter(ChatMessageModel.conversation_id == conversation_id).all()

    attached_documents = DocumentModel.query.filter(DocumentModel.conversation_id == conversation_id).all()

    return render_template('chat.html', messages=messages, attached_documents=attached_documents)


@chat_bp.route('/new', methods=['GET'])
def new():
    new_conversation = ConversationModel(title="Conversation")
    db.session.add(new_conversation)
    db.session.commit()

    return redirect(url_for('webapp.chat.index', conversation_id=new_conversation.id))


@chat_bp.route('/delete/<int:current_conversation_id>/<int:to_delete_id>', methods=["GET"])
def delete(current_conversation_id: int, to_delete_id: int):
    if not ConversationModel.exists(current_conversation_id):
        print(f"Invalid active conversation during delete id: {current_conversation_id} Aborting delete")
        return redirect(url_for('webapp.chat.index'))

    if not ConversationModel.exists(to_delete_id):
        print(f"Conversation {to_delete_id} does not exist - cannot delete it")
        return redirect(url_for('webapp.chat.index'))

    db.session.delete(ConversationModel.query.filter(ConversationModel.id == to_delete_id).first())
    db.session.commit()

    if to_delete_id == current_conversation_id:
        return redirect(url_for('webapp.chat.index'))
    return redirect(url_for('webapp.chat.index', conversation_id=current_conversation_id))


@chat_bp.route('/send/<int:conversation_id>', methods=["POST"])
def send(conversation_id: int):
    if not ConversationModel.exists(conversation_id):
        return jsonify({"error": "Invalid conversation"}), 400

    message = request.form.get("message", None)

    if not message:
        return jsonify({"error": "Message not provided"}), 400

    url = Config.API_BASE_URL + url_for("api.index", conversation_id=conversation_id)

    response = requests.post(url, data={"query": message})

    try:
        responseJSON = response.json()

        if responseJSON.get("error", None):
            return jsonify({"error": responseJSON.get("error")})

        response_message = responseJSON.get("message", None)

        # Saving to the db
        new_message = ChatMessageModel(conversation_id=conversation_id, message=message, response=response_message)
        db.session.add(new_message)
        db.session.commit()

        print(response_message)

        return jsonify({"rag_response": response_message})

    except Exception as e:
        print(e)
        return jsonify({"error": "Unknown error occurred"}), 500