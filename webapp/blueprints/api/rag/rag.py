from pymupdf import Document
from werkzeug.datastructures import FileStorage
from sentence_transformers import SentenceTransformer
import pymupdf4llm
from . import vector_db


def process_document(conversation_id: int, document: FileStorage):
    """
    Process the document to extract relevant information.
    """
    db = vector_db.VectorDB()

    # Create a collection for the conversation
    db.create_collection(conversation_id, dimension=384) # 384 for all-MiniLM-L6-v2

    # Embedding
    fragments = __divide_document_into_fragments(document)
    data = __get_embeddings_with_texts(fragments)

    # Insert data into the vector database
    db.insert_data(conversation_id, data)


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


def process_query(conversation_id: int, query: str) -> list:
    """
    Process the query to extract relevant information. Returns the most relevant document.
    """
    db = vector_db.VectorDB()

    # Embedding
    query_embedding = [__get_embeddings_with_texts([query])[0]['embedding']]

    # Search the vector database
    results = db.search(conversation_id, query_embedding)
    result = db.rerank(results, query)

    return result