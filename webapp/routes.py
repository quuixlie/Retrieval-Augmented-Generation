from flask import Blueprint, redirect, url_for, render_template, request

from flask import Blueprint

from .chat import chat_bp
from .documents import documents_bp
from .configurations import cfg_bp

webapp_bp = Blueprint('webapp', __name__, template_folder="templates", static_url_path="/webapp",
                      static_folder="static")
webapp_bp.register_blueprint(documents_bp, url_prefix="/documents")
webapp_bp.register_blueprint(chat_bp, url_prefix="/chat")
webapp_bp.register_blueprint(cfg_bp, url_prefix="/cfg")


@webapp_bp.route('/')
def index():
    return redirect(url_for("webapp.cfg.index"))
