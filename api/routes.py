from pymupdf import Document
import logging

from typing import Annotated
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
import json

import RAG.rag_architectures.rag_architecture_factory as rag_factory
import RAG.config as rag_config
from api_config import ApiConfig
from rag_config_parser import map_members

api_router = APIRouter()
classic_rag = rag_factory.RAGArchitectureFactory("classic-rag", config=rag_config.config)

config_fields = []

for m in map_members(type(rag_config.config)):
    config_fields.append(m)


@api_router.get("/health")
async def health():
    return {"status": "ok"}


@api_router.get('/sync')
async def available_models():
    """
    Endpoint to allow frontend to synchronize their state (architectures, models, etc.)
    """

    ApiConfig.refresh_models()
    return {
        "models": ApiConfig.AVAILABLE_MODELS,
        "config_generic_fields":config_fields,
        # TODO :: Add support for architecture and configs
    }

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

    # If something breaks this may be the cause :)
    # if not classic_rag.can_process_query(conversation_id):
    #    raise HTTPException(status_code=400, detail={"error": "No documents uploaded"})

    try:
        response = classic_rag.process_query(conversation_id, query)
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail={"error": "Internal error when processing query"})

    answer = response['answer']
    contexts = response['contexts']

    return {"answer": answer, "contexts": contexts}


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

    if not files:
        raise HTTPException(status_code=400, detail={"error": "No files provided"})

    for file in files:
        if file.content_type != "application/json":
            logging.warn(f"File: {file.filename} doesn't have mime type set to 'application/json', skipping.")
            continue

        file_bytes = await file.read()
        doc = Document(stream=file_bytes, filetype="pdf")
        classic_rag.process_document(conversation_id, doc)

    return {"message": "Files uploaded"}


@api_router.delete('/delete/{conversation_id}')
async def delete_collection(conversation_id: int):
    """
    Deletes the collection with given id
    :param conversation_id: ID of the conversation
    :return: JSON with error at key "error" or success message at key "message"
    """
    classic_rag.remove_conversation(conversation_id)
    return {"message": "Collection deleted"}
