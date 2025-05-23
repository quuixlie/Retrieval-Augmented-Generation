from flask import Flask, redirect, url_for
from flask_migrate import Migrate

from extensions import db,socketio


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

    app = Flask(__name__, static_folder="static", template_folder="templates")
    register_cli_arguments(app)

    # Loading configuration
    from app_config import AppConfig
    AppConfig.initialize()
    app.config.from_object(AppConfig)

    # Loading flask submodules
    print("Initializing database connection")
    db.init_app(app)
    print("Initializing database connection")
    _ = Migrate(app, db)

    socketio.init_app(app)

    # Registering blueprints and routes
    from blueprints.chat import chat_bp
    from blueprints.configurations import cfg_bp
    from blueprints.documents import documents_bp

    app.register_blueprint(documents_bp, url_prefix="/documents")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(cfg_bp, url_prefix="/cfg")

    # Ensuring the database exists
    AppConfig.create_db(app, db)

    # Registering callbacks
    @app.errorhandler(404)
    def not_found(error):
        return redirect(url_for("cfg.index"))

    @app.errorhandler(500)
    def internal_error(error):
        return error.get_response(), 500

    # Injecting conversation list for each template
    @app.context_processor
    def inject_conversations():
        from blueprints.models import ConversationModel
        conversations = ConversationModel.query.all()
        return dict(conversations=conversations)

    print("Application initialized")
    return app


if __name__ == '__main__':
    create_app().run("127.0.0.1", port=6942, debug=True)
