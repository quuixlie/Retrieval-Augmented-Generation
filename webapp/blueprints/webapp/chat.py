from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from app import db
from .models import ChatMessageModel
from session_data import get_session

chat_bp = Blueprint("chat", __name__)


@chat_bp.route('/', methods=["GET"])
def index():
    sess = get_session()['active_session_name'] if get_session()['active_session_name'] else None

    # print("session", sess)
    chat_sessions = [
        {"id": 1, "title": "Dialog 1"},
        {"id": 2, "title": "Dialog 2"},
    ]

    messages = []
    if sess:
        messages = ChatMessageModel.query.filter(ChatMessageModel.session_name == sess).all()

    return render_template('chat.html', messages=messages, active_session=sess,  chat_sessions=chat_sessions)


@chat_bp.route('/send', methods=["POST"])
def send():
    sess = get_session()['active_session_name'] if get_session()['active_session_name'] else None

    if not sess:
        return jsonify({"error": "No active session"}), 400

    message = request.form.get("message", None)

    if not message:
        return jsonify({"error": "Message not provided"}), 400

    # Todo :: Implement sending requests to RAG api
    response = "Some test rag response"

    try:
        new_message = ChatMessageModel(session_name=sess, message=message, response=response)
        db.session.add(new_message)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify({"error": "Unknown error occurred"}), 500

    return jsonify({"rag_response": response})
