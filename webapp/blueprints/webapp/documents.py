from flask import Blueprint, render_template, request, redirect, url_for

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


@documents_bp.route('/add', methods=["POST"])
def add():
    files = request.files.getlist("files")

    # TODO :: Process the files and ?save them to db?

    return redirect(url_for("webapp.documents.index", success=False, msg="NOT IMPLEMENTED"))


@documents_bp.route('/delete', methods=["POST"])
def delete():
    # TODO :: Delete the document from the db
    return redirect(url_for("webapp.documents.index", success=False, msg="NOT IMPLEMENTED"))
