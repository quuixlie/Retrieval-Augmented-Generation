from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__, template_folder="templates")


@api_bp.route('/')
def index():
    return jsonify({"message": "Message from rag"})
