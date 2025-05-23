from fastapi import FastAPI


def create_api():
    api = FastAPI()

    from api_config import ApiConfig
    ApiConfig.initialize()

    import routes
    api.include_router(routes.api_router)

    return api


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_api, host="0.0.0.0", port=8081, factory=True)
