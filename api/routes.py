from flask import Blueprint, jsonify, request, json
from .rag import rag
from webapp.llm_handler import llm, create_prompt, format_relevant_documents, format_response

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

    if not query:
        return jsonify({"error": "Query not provided"}), 400

    if not config:
        return jsonify({"error": "Config not provided"}), 400

    if not rag.can_process_query(conversation_id):
        return jsonify({"error": "No documents uploaded"}), 400

    # Get relevant documents and create prompt
    relevant_documents = rag.process_query(conversation_id, query)
    relevant_documents_formatted = format_relevant_documents(relevant_documents)
    prompt = create_prompt(query, relevant_documents_formatted)

    # Send it to the LLM and get the response
    model_endpoint = config['model_id']
    if (model_endpoint != "localhost"):
        response = llm(model_endpoint, prompt)
    else:
        response = "Local LLM not supported yet"

    # Format the response
    response = format_response(response, relevant_documents_formatted)

    return jsonify({"message": f"{response}"}), 200


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
        rag.process_document(conversation_id, file)

    return jsonify({"message": "Files uploaded"}), 200


@api_bp.route('/delete/<int:conversation_id>', methods=["delete"])
def delete_collection(conversation_id: int):
    """
    Deletes the collection with given id
    :param conversation_id: ID of the conversation
    :return: JSON with error at key "error" or success message at key "message"
    """

    db = rag.vector_db.VectorDB()
    db.remove_collection(conversation_id)


    return jsonify({"message": "Collection deleted"}), 200
