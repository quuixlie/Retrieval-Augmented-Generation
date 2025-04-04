from pymupdf import Document
from werkzeug.datastructures import FileStorage
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import MarkdownTextSplitter
import pymupdf4llm
from . import vector_db
from openai import OpenAI


def process_document(conversation_id: int, document: FileStorage):
    """
    Process the document to extract relevant information.
    """
    db = vector_db.VectorDB()

    # Create a collection for the conversation
    collection_name = f"conversation_{conversation_id}"
    db.create_collection(collection_name, dimension=384) # 384 for all-MiniLM-L6-v2

    # Embedding
    fragments = __divide_document_into_fragments(document)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    data = []

    for fragment in fragments:
        embedding = model.encode(fragment)

        data.append({
            "text": fragment,
            "embedding": embedding.tolist()
        })

    # Insert data into the vector database
    db.insert_data(collection_name, data)


def __divide_document_into_fragments(document: FileStorage):
    """
    Divide the document into fragments for embedding.
    :param document: FileStorage
    :return: list of fragments
    """
    document = Document(stream = document.read(), filetype="pdf")
    parsed_document_to_markdown = pymupdf4llm.to_markdown(doc = document)

    # Split the document into fragments
    splitter = MarkdownTextSplitter()
    fragments = splitter.split_text(parsed_document_to_markdown)

    return fragments


def process_query(conversation_id: int, query: str):
    """
    Process the query to extract relevant information.
    """
    db = vector_db.VectorDB()

    # Recreate collection name
    collection_name = f"conversation_{conversation_id}"

    # Embedding
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = [model.encode(query).tolist()]

    # Search the vector database
    results = db.search(collection_name, query_embedding)
    result = ""

    for result in results:
        for item in result:
            result = item["entity"]["text"]

    # Send request to LLM
    response = __get_response_from_llm(query, result)

    return response


def __get_response_from_llm(prompt: str, document: str):
    initial_prompt = """"Jestes nikim. Kim jestes? Jestes frajerem. Kim jestes? Odpowiedz na pytania."""
    api_key = "Buy your own API ACCESS NIGGERS"

    # Create a prompt in proper format
    prompt = initial_prompt + "<ZASOB_ZEWNETRZNY> " + document + "</ZASOB_ZEWNETRZNY>"

    openai_client = OpenAI(
        api_key = api_key
    )

    response = openai_client.responses.create(
        model="gpt-3.5-turbo",
        instructions=initial_prompt,
        input=prompt
    )

    return response.output_text

