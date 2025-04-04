import time
from time import sleep

import pymupdf
import pymupdf4llm
import requests
import os
from uuid import UUID

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

from app import db
from blueprints.webapp.models import ConversationModel, DocumentModel
from config import Config
from session_data import get_session

documents_bp = Blueprint("documents", __name__)


@documents_bp.route('/', methods=["GET"])
def index():
    # Set when the user tried to create,modify or select a session
    action_success = request.args.get("success", None, type=lambda x: x == "True")
    action_msg = request.args.get("msg", None)

    # TODO :: Query the documents from the db
    documents = ["TEST_DOC1", "TEST_DOC2", "TEST_DOC3", "TEST_DOC4", "TEST_DOC5"]

    active_session = get_session()['active_session_name'] if get_session()['active_session_name'] else None

    return render_template('documents.html', active_session=active_session, documents=documents,
                           action_success=action_success, action_msg=action_msg)


@documents_bp.route('/upload/<int:conversation_id>', methods=["POST"])
def upload(conversation_id: int):
    if not ConversationModel.exists(conversation_id):
        return jsonify({"error": "Conversation does not exist"})

    files = request.files.getlist("files")

    print("files:", files)

    for file in files:
        path_name = secure_filename(str(UUID(bytes=os.urandom(16))) + ".pdf")
        while DocumentModel.exists_with_path(path_name):
            path_name = secure_filename(str(UUID(bytes=os.urandom(16))) + ".pdf")

        document = DocumentModel(conversation_id=conversation_id, name=file.filename, path=path_name)

        path = os.path.join(Config.UPLOAD_DIRECTORY, path_name)

        try:

            file.save(path)

            # Resetting the cursor to allow reading the file again
            file.seek(0)

            db.session.add(document)
            db.session.commit()
        except Exception as e:
            print(e)
            return jsonify({"error": "Unknown error occurred"}), 500

    url = Config.API_BASE_URL + url_for("api.upload_documents", conversation_id=conversation_id)
    response = requests.post(url, files=[("files", file) for file in files])

    try:
        json = response.json()

        print(json)

        if json.get("error", None):
            return jsonify({"error": json.get("error")})

        conv_docs = DocumentModel.query.filter(DocumentModel.conversation_id == conversation_id).all()

        return render_template("chat_file_list.html", attached_documents=conv_docs), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Unknown error occurred"}), 500


@documents_bp.route('/delete', methods=["POST"])
def delete():
    # TODO :: Delete the document from the db
    return redirect(url_for("webapp.documents.index", success=False, msg="NOT IMPLEMENTED"))
