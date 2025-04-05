from pymupdf import Document
from werkzeug.datastructures import FileStorage
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
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
    data = __get_embeddings_with_texts(fragments)

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
    fragments = split_fixed_chunks(parsed_document_to_markdown)

    return fragments


def split_fixed_chunks(text, chunk_size=256):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def __get_embeddings_with_texts(fragments: list):
    """
    Get embeddings for the fragments.
    :param fragments: list of fragments
    :return: list of embeddings
    """
    model = SentenceTransformer("all-MiniLM-L12-v2")
    embeddings = []

    for fragment in fragments:
        embedding = model.encode(fragment)
        embeddings.append({
            "text": fragment,
            "embedding": embedding.tolist()
        })

    return embeddings


def process_query(conversation_id: int, query: str):
    """
    Process the query to extract relevant information.
    """
    db = vector_db.VectorDB()

    # Recreate collection name
    collection_name = f"conversation_{conversation_id}"

    # Embedding
    query_embedding = [__get_embeddings_with_texts([query])[0]['embedding']]

    # Search the vector database
    results = db.search(collection_name, query_embedding)
    result = db.rerank(results, query)

    response = __get_response_from_llm(query, result)

    return response


def __get_response_from_llm(prompt: str, document: str):
    initial_prompt = """You will get a prompt in the format: QUESTION <START_PROBABLY_HELPFUL_TEXT> CONTENT HERE <END_PROBABLY_HELPFUL_TEXT>. Answer as briefly as possible. Use the help text only if you don't know the answer yourself."""
    api_key = ""

    # Create a prompt in proper format
    prompt = prompt + " <START_PROBABLY_HELPFUL_TEXT>" + document + "<END_PROBABLY_HELPFUL_TEXT>"

    openai_client = OpenAI(
        api_key = api_key
    )

    response = openai_client.responses.create(
        model="gpt-3.5-turbo",
        instructions=initial_prompt,
        input=prompt
    )

    output = f"{response.output_text}\n\n\n" + "Based on: \n" + document
    return output

