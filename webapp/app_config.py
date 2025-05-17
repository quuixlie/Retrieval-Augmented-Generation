import os

import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class AppConfig:
    """
    Configuration class for the application

    The user must call the initialize method to initialize the configuration
    """
    SECRET_KEY = None
    UPLOAD_DIRECTORY = os.path.join("instance", "uploads")

    """These should be set through environment variables"""
    SQLALCHEMY_DATABASE_URI = None
    API_BASE_URL = None

    """
    List of available models
    """
    AVAILABLE_MODELS = []

    @staticmethod
    def initialize() -> None:
        """
        Initializes the configuration
        """
        print("Initializing AppConfig")

        AppConfig.__load_env()
        AppConfig.__read_secret_key()
        AppConfig.__get_available_models()

        print("Initialized AppConfig")

    @staticmethod
    def __load_env():
        """
        Loads envvars
        :return:
        """

        AppConfig.SQLALCHEMY_DATABASE_URI = os.getenv("DB_CONNECTION_STRING")
        AppConfig.API_BASE_URL = os.getenv("API_BASE_URL")

        if not AppConfig.SQLALCHEMY_DATABASE_URI:
            print("DB_CONNECTION_STRING Environment variable not set - terminal error exiting")
            exit(-1)

        if not AppConfig.API_BASE_URL:
            print("API_BASE_URL Environment variable not set - terminal error exiting")
            exit(-1)

    @staticmethod
    def __read_secret_key():
        """
        Reads the secret key from the file
        """
        print("Reading secret key")
        try:
            with open("instance/secret_key", "r") as file:
                AppConfig.SECRET_KEY = file.read().strip()
        except OSError:
            print("Secret key file not found - creating new one")
            # Secret file doesn't exist
            if not os.path.exists("instance"):
                os.makedirs("instance")

            with open("instance/secret_key", "w") as file:
                secret_key = str(os.urandom(32))
                file.write(secret_key)
                AppConfig.SECRET_KEY = secret_key

        print("Secret key loaded")

    @staticmethod
    def __get_available_models():
        """
        Gets the available models from the API
        """

        print("Getting available models")
        try:
            response = requests.get(f"{AppConfig.API_BASE_URL}/available_models", timeout=3)
            if response.status_code == 200:
                AppConfig.AVAILABLE_MODELS = response.json()["models"]
                print("Available models loaded")
            else:
                print("Error loading available models - terminal error exiting")
                exit(-1)
        except requests.exceptions.RequestException as e:
            print(f"Error loading available models: {e}")

    @staticmethod
    def __create_default_config_entity(app: Flask, db: SQLAlchemy):

        print("Creating default configuration")
        # Create default config
        from blueprints.models import ConfigModel
        with app.app_context():

            configs = ConfigModel.get_all()
            print("Configs:",configs)

            model_id = AppConfig.AVAILABLE_MODELS[0]['id'] if len(
                AppConfig.AVAILABLE_MODELS) > 0 else "deepseek/deepseek-chat-v3-0324:free"

            model_name = AppConfig.AVAILABLE_MODELS[0]['name'] if len(
                AppConfig.AVAILABLE_MODELS) > 0 else "DeepSeek: DeepSeek V3 0324 (free)"

            default_config = ConfigModel(id=0, name="Default", model_id=model_id,
                                         model_name=model_name, chunk_size=100,is_default=True)

            db.session.add(default_config)
            db.session.commit()
            print("Default configuration created: ", default_config.get_values_dict())

    @staticmethod
    def create_db(app: Flask, db: SQLAlchemy):
        """
        Creates the database instance if it doesn't exist
        :param app: Flask application instance
        :param db: SQLAlchemy instance
        """

        if not os.path.exists("instance"):
            os.makedirs("instance")

        with app.app_context():
            db.create_all()
            print("Created tables: ", db.Model.metadata.tables.keys())

            from blueprints.models import ConfigModel
            # Ensuring default config is in the db
            try:
                ConfigModel.get_default()
            except ValueError:
                print("Default config not found in the database - creating new one")
                # Create default config
                AppConfig.__create_default_config_entity(app, db)
            except Exception as e:
                print("Couldn't create default configuration", e)

            print("Database created")
