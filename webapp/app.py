from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import session

import session_data
from session_data import SessionData

db = SQLAlchemy()


def create_app() -> Flask:
    """
    Main application factory.
    Creates the Flask app and returns it.
    :return: Flask
    """

    app = Flask(__name__)

    # Loading configuration
    from config import Config
    Config.initialize()
    app.config.from_object(Config)

    # Loading flask submodules
    db.init_app(app)
    migrate = Migrate(app, db)

    # Registering blueprints and routes
    from blueprints import webapp_bp
    from blueprints import api_bp

    app.register_blueprint(webapp_bp, url_prefix="/")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Ensuring the database exists
    Config.create_db(app, db)

    # Registering callbacks
    @app.errorhandler(404)
    def not_found(error):
        return error.get_response(), 404

    @app.errorhandler(500)
    def internal_error(error):
        return error.get_response(), 500

    @app.before_request
    def before_request():
        if len(session.keys()) == 0:
            for k, v in session_data.default_session_data().items():
                session.setdefault(k, v)

    # Injecting conversations list to every template so it doesn't have to be manually passed
    from blueprints.webapp.models import ConversationModel

    @app.context_processor
    def inject_conversations():
        conversations = ConversationModel.query.all()
        return dict(conversations=conversations)

    return app


if __name__ == '__main__':
    create_app().run("127.0.0.1", port=6942, debug=True)
