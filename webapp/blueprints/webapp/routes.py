from flask import Blueprint, redirect, url_for, render_template, request

webapp = Blueprint('webapp', __name__, template_folder="templates", static_url_path="/webapp", static_folder="static")


@webapp.route('/')
def index():
    return redirect(url_for('webapp.settings'))


@webapp.route('/settings', methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        print(request.form)

    elif request.method == "GET":
        return render_template('settings.html')


@webapp.route('/sessions', methods=["GET"])
def sessions():
    return render_template('sessions.html')


@webapp.route('/documents', methods=["GET"])
def documents():
    return render_template('documents.html')


@webapp.route('/chat', methods=["GET"])
def chat():
    return render_template('chat.html')
