import requests
from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from app import db
from appconfig import AppConfig
from .models import ChatMessageModel, ConversationModel, DocumentModel, ConfigModel

chat_bp = Blueprint("chat", __name__)


@chat_bp.route('/<int:conversation_id>', methods=["GET"])
def index(conversation_id: int):
    """
    The main chat page that lets the user query and upload files to the model.

    GET Parameters:
    err: [Optional] error message to display to the user as a simple popup.
    """

    error_msg = request.args.get("err", None)

    conversation = ConversationModel.query.filter(ConversationModel.id == conversation_id).first()

    if not conversation:
        return redirect(url_for('.new'))

    messages = ChatMessageModel.query.filter(ChatMessageModel.conversation_id == conversation_id).all()

    attached_documents = DocumentModel.query.filter(DocumentModel.conversation_id == conversation_id).all()

    active_configuration = conversation.active_config
    all_configurations = ConfigModel.query.all()

    return render_template('chat.html', conversation_id=conversation_id, messages=messages,
                           attached_documents=attached_documents,
                           active_configuration=active_configuration,
                           all_configurations=all_configurations,
                           popup_success=False if error_msg else None,
                           popup_msg=error_msg)


@chat_bp.route('/new', methods=['GET'])
def new():
    """
    Creates a new conversation and redirects to the chat page.

    GET Parameters:
    config_id: [Optional] configuration id to use for the new conversation.
                The conversation id must be valid otherwise default configuration will be used.
    """

    config_id = request.args.get("config_id", type=int)

    if config_id and not ConfigModel.exists(config_id):
        config_id = None

    # Default config
    if not config_id:
        config_id = ConfigModel.get_default().id

    new_conversation = ConversationModel(title="Conversation", active_config_id=config_id)
    db.session.add(new_conversation)
    db.session.commit()

    print(f"Created new conversation with id: {new_conversation.id}")

    return redirect(url_for('.index', conversation_id=new_conversation.id))


@chat_bp.route("/change_config/<int:conversation_id>/<int:config_id>", methods=["GET"])
def change_config(conversation_id: int, config_id: int):
    """
    Changes the active configuration for given conversation.

    URL Parameters:
    conversation_id: The id of the conversation to change the configuration for.
    config_id: The id of the configuration to set as active. If configuration is not valid (entity does not exist),
               conversation remains unchanged and user is redirected to configuration list page.
    """
    conversation = ConversationModel.query.filter(ConversationModel.id == conversation_id).first()

    if not conversation:
        return redirect(url_for('.new', config_id=config_id))

    if not ConfigModel.exists(config_id):
        return redirect(url_for(".index", err="Provided configuration is not valid"))

    # Update the active config
    conversation.active_config_id = config_id
    db.session.commit()

    return redirect(url_for('.index', conversation_id=conversation_id))


@chat_bp.route('/delete/<int:id>', methods=["DELETE"])
def delete(id: int):
    """
    Deletes the conversation with given id
    """
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
    """
    Sends a message to the model and returns its response.

    return:
        In case of error returns JSON with this struct:
            {
                "error": string_error_message_
            }
        In case of success returns JSON with this struct:
            {
                "rag_response": string_response_from_rag
            }
    """
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
