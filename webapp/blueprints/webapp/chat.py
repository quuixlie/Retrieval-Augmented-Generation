from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from app import db
from .models import ChatMessageModel, ConversationModel
from session_data import get_session

chat_bp = Blueprint("chat", __name__)


@chat_bp.route('/', methods=["GET"])
def index():
    # Empty chat
    return render_template('chat.html')


@chat_bp.route('/<int:conversation_id>', methods=["GET"])
def chat(conversation_id: int):
    conversation = ConversationModel.query.filter(ConversationModel.id == conversation_id).first()

    if not conversation:
        return redirect(url_for('webapp.sessions.index', success=False, msg="Conversation does not exist"))

    messages = ChatMessageModel.query.filter(ChatMessageModel.conversation_id == conversation_id).all()

    return render_template('chat.html', messages=messages)


@chat_bp.route('/new', methods=['GET'])
def new():
    new_conversation = ConversationModel(title="New conversation")
    db.session.add(new_conversation)
    db.session.commit()

    return redirect(url_for('webapp.chat.chat', conversation_id=new_conversation.id))


@chat_bp.route('/send/<int:conversation_id>', methods=["POST"])
def send(conversation_id: int):
    conversation_exists = ConversationModel.query.filter(ConversationModel.id == conversation_id).first()

    if not conversation_exists:
        return jsonify({"error": "Invalid conversation"}), 400

    message = request.form.get("message", None)

    if not message:
        return jsonify({"error": "Message not provided"}), 400

    # Todo :: Implement sending requests to RAG api

    response = "Some test rag response"

    try:
        new_message = ChatMessageModel(conversation_id=conversation_id, message=message, response=response)
        db.session.add(new_message)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify({"error": "Unknown error occurred"}), 500

    return jsonify({"rag_response": response})
