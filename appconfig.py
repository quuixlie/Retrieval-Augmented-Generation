import os
import re

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
    MILVUS_URL = None
    API_BASE_URL = None
    OPENROUTER_API_KEY = None

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
        AppConfig.__set_available_models()

        print("Initialized AppConfig")

    @staticmethod
    def __load_env():
        """
        Loads envvars
        :return:
        """

        AppConfig.SQLALCHEMY_DATABASE_URI = os.getenv("DB_CONNECTION_STRING")
        AppConfig.MILVUS_URL = os.getenv("MILVUS_URL")
        AppConfig.API_BASE_URL = os.getenv("API_BASE_URL")
        AppConfig.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

        if not AppConfig.SQLALCHEMY_DATABASE_URI:
            print("DB_CONNECTION_STRING Environment variable not set - terminal error exiting")
            exit(-1)

        if not AppConfig.MILVUS_URL:
            print("MILVUS_URL Environment variable not set - terminal error exiting")
            exit(-1)

        if not AppConfig.API_BASE_URL:
            print("API_BASE_URL Environment variable not set - terminal error exiting")
            exit(-1)

        if not AppConfig.OPENROUTER_API_KEY:
            print("OPENROUTER_API_KEY Environment variable not set - terminal error exiting")
            exit(-1)

    @staticmethod
    def __set_available_models():
        """
        Sets the available models
        """
        # Getting only the free models

        response = requests.get("https://openrouter.ai/api/v1/models")

        if not response.ok:
            print("Couldn't fetch available models from openrouter")
            return
        try:
            models = response.json()["data"]
            pattern = "^.*:free$"

            models = [model for model in models if re.match(pattern, model["id"])]
            models.append({'id': 'localhost',
                           'name': '#to_wcale_nie_jest_koparka_btc_to_tylko_rag_okok',
                           'description': '#to_wcale_nie_jest_koparka_btc_to_tylko_rag_okok'})
            models.sort(key=lambda x: x["name"])
            AppConfig.AVAILABLE_MODELS = models

            # print doesn't work with utf-8 encoded data on windows (default encoding is cp1250)
            import sys
            previous_encoding = sys.stdout.encoding
            sys.stdout.reconfigure(encoding="utf-8")
            print(f"Received {len(models)} models from openrouter")
            sys.stdout.reconfigure(encoding=previous_encoding)

        except Exception as e:
            print(f"Error occurred while fetching models: {e}")
            return

    @staticmethod
    def __create_upload_directory():
        """
        Creates the upload directory if it doesn't exist
        """
        print("Creating upload directory")
        if not os.path.exists(AppConfig.UPLOAD_DIRECTORY):
            print("Upload directory created")
            os.makedirs(AppConfig.UPLOAD_DIRECTORY)
        else:
            print("Upload directory already exists no need to create it")

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
    def __create_default_config_entity(app: Flask, db: SQLAlchemy):

        print("Creating default configuration")
        # Create default config
        from webapp.models import ConfigModel
        with app.app_context():
            default_config = ConfigModel(id=0, name="Default", model_id=AppConfig.AVAILABLE_MODELS[0]['id'] if len(
                AppConfig.AVAILABLE_MODELS) > 0 else "google/gemini-2.5-pro-exp-03-25:free",
                                         model_name=AppConfig.AVAILABLE_MODELS[0]['name'], chunk_size=100,
                                         document_count=5, is_default=True)

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
            # db.drop_all()
            db.create_all()
            print(db.metadata.tables.keys())

            print("Database successfully created")
            # Ensuring default config is in the db
            from webapp.models import ConfigModel
            try:
                ConfigModel.get_default()
            except ValueError as e:
                print("Default config not found in the database - creating new one")
                # Create default config
                AppConfig.__create_default_config_entity(app, db)

            except Exception as e:
                print("TERMINAL ERROR:: Couldn't create default configuration", e)
