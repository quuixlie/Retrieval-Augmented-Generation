import os
import re

import requests


class ApiConfig:
    DB_URL: str | None = None
    OPENROUTER_API_KEY: str | None = None
    AVAILABLE_MODELS = []

    @staticmethod
    def initialize():
        """
        Initializes the configuration
        """
        print("Initializing ApiConfig")

        ApiConfig.__load_env()
        ApiConfig.__set_available_models()

        print("Initialized ApiConfig")

    @staticmethod
    def __load_env():
        """
        Loads envvars
        """

        ApiConfig.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        ApiConfig.DB_URL = os.getenv("DB_URL")

        if not ApiConfig.DB_URL:
            print("MILVUS_URL Environment variable not set - terminal error exiting")
            exit(-1)

        if not ApiConfig.OPENROUTER_API_KEY:
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

            ApiConfig.AVAILABLE_MODELS = models
        except Exception as e:
            print(f"Error occurred while fetching models: {e}")
            return
