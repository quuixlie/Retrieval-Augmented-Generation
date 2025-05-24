import logging
import os
import re

import requests


class ApiConfig:
    DB_URL: str | None = None
    OPENAI_API_KEY: str | None = None
    AVAILABLE_MODELS = []

    @staticmethod
    def initialize():
        """
        Initializes the configuration
        """
        logging.info("Initializing ApiConfig")

        ApiConfig.__load_env()
        ApiConfig.refresh_models()

        logging.info("Initialized ApiConfig")

    @staticmethod
    def __load_env():
        """
        Loads envvars
        """

        ApiConfig.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        ApiConfig.DB_URL = os.getenv("DB_URL")

        if not ApiConfig.DB_URL:
            logging.critical("DB_URL Environment variable not set - terminal error exiting")
            exit(-1)

        if not ApiConfig.OPENAI_API_KEY:
            logging.critical("OPENAI_API_KEY Environment variable not set - terminal error exiting")
            exit(-1)


    @staticmethod
    def refresh_models():
        """
        Sets the available models
        """
        # Getting only the free models

        response = requests.get("https://openrouter.ai/api/v1/models")

        if not response.ok:
            logging.error("Couldn't fetch available models from openrouter")
            return
        try:
            models = response.json()["data"]
            pattern = "^.*:free$"

            models = [model for model in models if re.match(pattern, model["id"])]
            models.append({'id': 'localhost',
                           'name': '#to_wcale_nie_jest_koparka_btc_to_tylko_rag_okok',
                           'description': '#to_wcale_nie_jest_koparka_btc_to_tylko_rag_okok'})
            models.sort(key=lambda x: x["name"])

            ApiConfig.AVAILABLE_MODELS = models
        except Exception as e:
            logging.error(f"Error occurred while fetching models: {e}")
            return
