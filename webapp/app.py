from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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
    Config.create_db(app, db)
    migrate = Migrate(app, db)

    # Registering blueprints and routes
    from blueprints import webapp
    from blueprints import api

    app.register_blueprint(webapp, url_prefix="/")
    app.register_blueprint(api, url_prefix="/api")

    # Registering callbacks
    @app.errorhandler(404)
    def not_found(error):
        return error.get_response(), 404

    @app.errorhandler(500)
    def internal_error(error):
        return error.get_response(), 500

    return app


if __name__ == '__main__':
    create_app().run("127.0.0.1", port=6942, debug=True)
