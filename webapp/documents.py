import requests
import os
from uuid import UUID

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, json
from werkzeug.utils import secure_filename

from app import db
from webapp.models import ConversationModel, DocumentModel
from appconfig import AppConfig

documents_bp = Blueprint("documents", __name__)


@documents_bp.route('/upload/<int:conversation_id>', methods=["POST"])
def upload(conversation_id: int):
    conversation = ConversationModel.query.filter(ConversationModel.id == conversation_id).first()

    if not conversation:
        return jsonify({"error": "Conversation does not exist"})

    files = request.files.getlist("files")

    for file in files:
        path_name = secure_filename(str(UUID(bytes=os.urandom(16))) + ".pdf")
        while DocumentModel.exists_with_path(path_name):
            path_name = secure_filename(str(UUID(bytes=os.urandom(16))) + ".pdf")

        document = DocumentModel(conversation_id=conversation_id, name=file.filename, path=path_name)

        path = os.path.join(AppConfig.UPLOAD_DIRECTORY, path_name)

        try:
            file.save(path)

            # Resetting the cursor to allow reading the file again
            file.seek(0)

            db.session.add(document)
            db.session.commit()
        except Exception as e:
            print(e)
            return jsonify({"error": "Unknown error occurred"}), 500

    url = AppConfig.API_BASE_URL + url_for("api.upload_documents", conversation_id=conversation_id)

    config_dict = conversation.active_config.get_values_dict()

    multipart_data = [("files", (file.filename, file, "application/pdf")) for file in files]
    multipart_data += [("config", ("config", json.dumps(config_dict), "application/json"))]

    response = requests.post(url, files=multipart_data)

    try:
        ragJSON = response.json()

        print(ragJSON)

        if ragJSON.get("error", None):
            return jsonify({"error": ragJSON.get("error")})

        conv_docs = DocumentModel.query.filter(DocumentModel.conversation_id == conversation_id).all()

        return render_template("chat_file_list.html", attached_documents=conv_docs), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Unknown error occurred"}), 500


@documents_bp.route('/delete', methods=["POST"])
def delete():
    # TODO :: Delete the document from the db
    return redirect(url_for("webapp.documents.index", success=False, msg="NOT IMPLEMENTED"))
