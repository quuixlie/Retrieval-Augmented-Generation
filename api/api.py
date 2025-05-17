from fastapi import FastAPI

db = None


def create_api():
    api = FastAPI()

    from api_config import ApiConfig
    ApiConfig.initialize()

    from rag.vector_db import VectorDB

    global db
    db = VectorDB()

    import routes
    api.include_router(routes.api_router)



    return api






