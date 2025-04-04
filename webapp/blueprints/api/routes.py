from flask import Blueprint, jsonify, request
from .rag import rag_input


api_bp = Blueprint("api", __name__)


@api_bp.route('/query/<int:conversation_id>', methods=["POST"])
def index(conversation_id: int):
    """
    Query the RAG API
    :return: JSON with RAG response at key "message" or error at key "error"
    """

    query = request.form.get("query", None)

    if not query:
        return jsonify({"error": "Query not provided"}), 400

    # Process the query
    result = rag_input.process_query(conversation_id, query)

    return jsonify({"message": f"{result}"}), 200


#
@api_bp.route('/upload/<int:conversation_id>', methods=["POST"])
def upload_documents(conversation_id: int):
    """
    Uploads files to RAG
    :param conversation_id: ID of the conversation
    :return: JSON with error at key "error" or success message at key "message"
    """

    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files provided"}), 400

    for file in files:
        rag_input.process_document(conversation_id, file)

    return jsonify({"message": "Files uploaded"}), 200
