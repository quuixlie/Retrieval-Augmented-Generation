import requests

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, json

from extensions import db
from app_config import AppConfig
from .models import ConversationModel, DocumentModel

documents_bp = Blueprint("documents", __name__, static_folder="static", template_folder="templates")


@documents_bp.route('/upload/<int:conversation_id>', methods=["POST"])
def upload(conversation_id: int):
    conversation = ConversationModel.query.filter(ConversationModel.id == conversation_id).first()

    if not conversation:
        return jsonify({"error": "Conversation does not exist"})

    files = request.files.getlist("files")

    url = f"{AppConfig.API_BASE_URL}/upload/{conversation_id}"
    config_dict = conversation.active_config.get_values_dict()

    multipart_data = [("files", (file.filename, file, "application/pdf")) for file in files]
    multipart_data += [("config", ("config", json.dumps(config_dict), "application/json"))]

    response = requests.post(url, files=multipart_data)

    try:
        ragJSON = response.json()

        print(ragJSON)

        if ragJSON.get("error", None):
            return jsonify({"error": ragJSON.get("error")})

        # Uploading files to the database only on success rag response
        for file in files:
            document = DocumentModel(conversation_id=conversation_id, name=file.filename)
            try:
                db.session.add(document)
                db.session.commit()
            except Exception as e:
                print(e)
                return jsonify({"error": "Unknown error occurred"}), 500

        conv_docs = DocumentModel.query.filter(DocumentModel.conversation_id == conversation_id).all()

        return render_template("chat_file_list.html", attached_documents=conv_docs), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Unknown error occurred"}), 500


@documents_bp.route('/delete', methods=["POST"])
def delete():
    # TODO :: Delete the document from the db
    return redirect(url_for(".index", success=False, msg="NOT IMPLEMENTED"))
