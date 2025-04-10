from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import session

import session_data

db = SQLAlchemy()


def register_cli_arguments(app: Flask) -> None:
    """
    Registers CLI arguments for the application.
    :param app: Flask application
    """

    @app.cli.command("drop-db")
    def drop_db() -> None:
        """
        Drops all tables in the database.
        """
        with app.app_context():
            db.drop_all()
            print(f"Database dropped")


def create_app() -> Flask:
    """
    Main application factory.
    Creates the Flask app and returns it.
    :return: Flask
    """

    app = Flask(__name__)

    register_cli_arguments(app)

    # Loading configuration
    from appconfig import AppConfig
    AppConfig.initialize()
    app.config.from_object(AppConfig)

    # Loading flask submodules
    print("Initializing database connection")
    db.init_app(app)
    print("Initializing database connection")
    migrate = Migrate(app, db)

    # Registering blueprints and routes
    from webapp.routes import webapp_bp
    from api.routes import api_bp

    app.register_blueprint(webapp_bp, url_prefix="/")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Ensuring the database exists
    AppConfig.create_db(app, db)

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
    from webapp.models import ConversationModel

    @app.context_processor
    def inject_conversations():
        conversations = ConversationModel.query.all()
        return dict(conversations=conversations)

    print("Application initialized")
    return app


if __name__ == '__main__':
    create_app().run("127.0.0.1", port=6942, debug=True)
