import asyncio

from flask import Blueprint, jsonify, request, json
from .rag import rag_input
from ..webapp.llm_handler import llm

api_bp = Blueprint("api", __name__)


@api_bp.route('/query/<int:conversation_id>', methods=["POST"])
def index(conversation_id: int):
    """
    Query the RAG API
    :return: JSON with RAG response at key "message" or error at key "error"
    """

    query = request.json.get("query", None)
    config = request.json.get("config", None)
    print("Query: ", query)
    print("Query config:", config)

    # {'model_id': 'meta-llama/llama-4-maverick:free', 'model_name': 'Meta: Llama 4 Maverick (free)', 'chunk_size': 100, 'document_count': 5}

    if not query:
        return jsonify({"error": "Query not provided"}), 400

    if not config:
        return jsonify({"error": "Config not provided"}), 400

    model_endpoint = config['model_id']

    data = llm(model_endpoint, query)

    # Process the query
    # result = rag_input.process_query(conversation_id, query)

    return jsonify({"message": f"{data}"}), 200


#
@api_bp.route('/upload/<int:conversation_id>', methods=["POST"])
def upload_documents(conversation_id: int):
    """
    Uploads files to RAG
    :param conversation_id: ID of the conversation
    :return: JSON with error at key "error" or success message at key "message"
    """

    files = request.files.getlist("files")
    config = request.files.get("config", None)

    if config:
        config = json.loads(config.read())

    print("Upload files: ", files)
    print("Upload files config: ", config)

    if not files:
        return jsonify({"error": "No files provided"}), 400

    for file in files:
        rag_input.process_document(conversation_id, file)

    return jsonify({"message": "Files uploaded"}), 200
