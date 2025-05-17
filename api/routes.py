from typing import Annotated
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
import json

import rag.rag as rag
import llm_handler as llm
from api_config import ApiConfig

api_router = APIRouter()


@api_router.get("/health")
def health():
    return {"status": "ok"}


@api_router.get('/available_models')
def available_models():
    return {"models": ApiConfig.AVAILABLE_MODELS}


class QueryModel(BaseModel):
    query: str | None = None
    config: dict | None = None


@api_router.post('/query/{conversation_id}')
async def index(conversation_id: int, parameters: QueryModel):
    """
    Query the RAG API
    :return: JSON with RAG response at key "message" or error at key "error"
    """

    query = parameters.query
    config = parameters.config
    print("Query: ", query)
    print("Query config:", config)

    if not query:
        raise HTTPException(status_code=400, detail={"error": "Query not provided"})

    if not config:
        raise HTTPException(status_code=400, detail={"error": "Config not provided"})

    if not rag.can_process_query(conversation_id):
        raise HTTPException(status_code=400, detail={"error": "No documents uploaded"})

    # Get relevant documents and create prompt
    relevant_documents = rag.process_query(conversation_id, query)
    relevant_documents_formatted = llm.format_relevant_documents(relevant_documents)
    prompt = llm.create_prompt(query, relevant_documents_formatted)

    # Send it to the LLM and get the response
    model_endpoint = config['model_id']
    if model_endpoint != "localhost":
        response = llm.llm(model_endpoint, prompt)

        if "error" in response:
            return HTTPException(status_code=500, detail={"error": response["error"]})

    else:
        response = "Local LLM not supported yet"

    # Format the response
    response = llm.format_response(response, relevant_documents_formatted)

    return {"message": response}


#
@api_router.post('/upload/{conversation_id}')
async def upload_documents(conversation_id: int, files: Annotated[list[UploadFile], []],
                           config: Annotated[UploadFile, File()]):
    """
    Uploads files to RAG
    :param files:
    :param config:
    :param conversation_id: ID of the conversation
    :return: JSON with error at key "error" or success message at key "message"
    """

    if config:
        content = config.file.read()
        config = json.loads(content)

    print("Upload files: ", files)
    print("Upload files config: ", config)

    if not files:
        raise HTTPException(status_code=400, detail={"error": "No files provided"})


    for file in files:
        rag.process_document(conversation_id, file.file)

    return {"message": "Files uploaded"}


@api_router.delete('/delete/{conversation_id}')
def delete_collection(conversation_id: int):
    """
    Deletes the collection with given id
    :param conversation_id: ID of the conversation
    :return: JSON with error at key "error" or success message at key "message"
    """
    db = rag.vector_db.VectorDB()
    db.remove_collection(conversation_id)
    return {"message": "Collection deleted"}
