from flask import Blueprint, render_template, request, url_for, redirect, session

from app import db
from blueprints.webapp.models import ConversationModel
from session_data import SessionData, get_session

sessions_bp = Blueprint('sessions', __name__)


@sessions_bp.route('/', methods=["GET"])
def index():
    # Set when the user tried to create,modify or select a session
    action_success = request.args.get("success", None, type=lambda x: x == "True")
    action_msg = request.args.get("msg", None)

    # Querying the names of the sessions
    session_names = [name for (name,) in ConversationModel.query.with_entities(ConversationModel.name).all()]

    active_session = get_session()['active_session_name'] if get_session()['active_session_name'] else None

    return render_template('sessions.html', sessions=session_names, action_success=action_success,
                           action_msg=action_msg, active_session=active_session)


@sessions_bp.route('/new', methods=['POST'])
def add():
    """
    Tries to create a new session and sets it as active if successful.
    redirects to sessions page with a "success" URL parameter set to True in case of success and False otherwise.
    """
    name = request.form.get("name", None)

    if not name:
        return redirect(url_for('webapp.sessions.index', success=False, msg="Name not provided"))

    already_exists = ConversationModel.query.filter(ConversationModel.name == name).first()

    if already_exists:
        return redirect(url_for('webapp.sessions.index', success=False, msg="Session already exists"))

    new_session = ConversationModel(name=name)
    db.session.add(new_session)
    db.session.commit()

    get_session()['active_session_name'] = new_session.name

    return redirect(url_for('webapp.sessions.index', success=True, msg=f"Session {name} created"))


@sessions_bp.route('/select', methods=['POST'])
def select():
    """
    Tries to select a session.
    redirects to sessions page with a "success" URL parameter set to True in case of success and False otherwise.
    """
    name = request.form.get("name", None)

    if not name:
        return redirect(url_for('webapp.sessions.index', success=False, msg="Name not provided"))

    new_session = ConversationModel.query.filter(ConversationModel.name == name).first()

    get_session().active_session_name = new_session.name

    return redirect(url_for('webapp.sessions.index', success=True, msg=f"Session {name} selected"))


@sessions_bp.route('/delete', methods=['POST'])
def delete():
    """
    Tries to delete a session.
    redirects to sessions page with a "success" URL parameter set to True in case of success and False otherwise.
    """
    name = request.form.get("name", None)

    if not name:
        return redirect(url_for('webapp.sessions.index', success=False, msg="Name not provided"))

    new_session = ConversationModel.query.filter(ConversationModel.name == name).first()
    db.session.delete(new_session)
    db.session.commit()

    if get_session()['active_session_name'] == name:
        get_session()['active_session_name'] = None

    return redirect(url_for('webapp.sessions.index', success=True, msg=f"Session {name} deleted"))
