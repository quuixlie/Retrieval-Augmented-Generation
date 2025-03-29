from flask import Blueprint, jsonify

api = Blueprint("api", __name__, template_folder="templates")


@api.route('/')
def index():
    return jsonify({"message": "Message from rag"})
