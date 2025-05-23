import os

import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import logging


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
        logging.info("Initializing AppConfig")

        AppConfig.__load_env()
        AppConfig.__read_secret_key()
        AppConfig.__sync_state()

        logging.info("Initialized AppConfig")

    @staticmethod
    def __load_env():
        """
        Loads envvars
        :return:
        """

        AppConfig.SQLALCHEMY_DATABASE_URI = os.getenv("DB_CONNECTION_STRING")
        AppConfig.API_BASE_URL = os.getenv("API_BASE_URL")

        if not AppConfig.SQLALCHEMY_DATABASE_URI:
            logging.critical("DB_CONNECTION_STRING Environment variable not set - terminal error exiting")
            exit(-1)

        if not AppConfig.API_BASE_URL:
            logging.critical("API_BASE_URL Environment variable not set - terminal error exiting")
            exit(-1)

    @staticmethod
    def __read_secret_key():
        """
        Reads the secret key from the file
        """
        logging.info("Reading secret key")
        try:
            with open("instance/secret_key", "rb") as file:
                AppConfig.SECRET_KEY = file.read().strip()
        except OSError:
            logging.info("Secret key file not found - creating new one")
            # Secret file doesn't exist
            if not os.path.exists("instance"):
                os.makedirs("instance")

            with open("instance/secret_key", "wb") as file:
                secret_key = bytearray(os.urandom(32))
                file.write(secret_key)
                AppConfig.SECRET_KEY = secret_key

        logging.info("Secret key loaded")

    @staticmethod
    def __sync_state():
        """
        Gets the available models from the API
        """

        logging.info("Getting available models")
        try:
            response = requests.get(f"{AppConfig.API_BASE_URL}/sync", timeout=15)
            if response.status_code == 200:
                AppConfig.AVAILABLE_MODELS = response.json()["models"]
                logging.info("Available models loaded")
            else:
                logging.critical("Error loading available models - terminal error exiting")
                exit(-1)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error loading available models: {e}")

    @staticmethod
    def __create_default_config_entity(app: Flask, db: SQLAlchemy):

        logging.info("Creating default configuration")
        # Create default config
        from blueprints.models import ConfigModel
        with app.app_context():

            model_id = AppConfig.AVAILABLE_MODELS[0]['id'] if len(
                AppConfig.AVAILABLE_MODELS) > 0 else "deepseek/deepseek-chat-v3-0324:free"

            model_name = AppConfig.AVAILABLE_MODELS[0]['name'] if len(
                AppConfig.AVAILABLE_MODELS) > 0 else "DeepSeek: DeepSeek V3 0324 (free)"

            default_config = ConfigModel(id=0, name="Default", model_id=model_id,
                                         model_name=model_name, chunk_size=100,is_default=True)

            db.session.add(default_config)
            db.session.commit()
            logging.info("Default configuration created: ", default_config.get_values_dict())

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
            from blueprints.models import ConfigModel
            # Ensuring default config is in the db
            try:
                ConfigModel.get_default()
            except ValueError:
                logging.info("Default config not found in the database - creating new one")
                # Create default config
                AppConfig.__create_default_config_entity(app, db)
            except Exception as e:
                logging.error("Couldn't create default configuration", e)

            logging.info("Database created")
