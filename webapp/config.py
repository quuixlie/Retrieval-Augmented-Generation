import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config:
    """
    Configuration class for the application

    The user must call the initialize method to initialize the configuration
    """
    SECRET_KEY = None
    SQLALCHEMY_DATABASE_URI = "sqlite:///db_instance.db"

    @staticmethod
    def initialize() -> None:
        """
        Initializes the configuration
        """

        Config.SECRET_KEY = Config.__read_secret_key()

    @staticmethod
    def __read_secret_key() -> str:
        """
        Reads the secret key from the file
        """
        try:
            with open("instance/secret_key", "r") as file:
                return file.read().strip()
        except OSError:
            # Secret file doesn't exist
            if not os.path.exists("instance"):
                os.makedirs("instance")

            with open("instance/secret_key", "w") as file:
                secret_key = str(os.urandom(32))
                file.write(secret_key)
                return secret_key

    @staticmethod
    def create_db(app: Flask, db: SQLAlchemy):
        """
        Creates the database instance if it doesn't exist
        :param app: Flask application instance
        :param db: SQLAlchemy instance
        """
        if not os.path.exists("instance"):
            os.makedirs("instance")

        if not os.path.exists("instance/db_instance.db"):
            print("Database doesn't instance doesn't exist - Creating new one")
            with app.app_context():
                db.create_all()
                print("Database successfully created")
