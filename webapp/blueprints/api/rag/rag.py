from pymupdf import Document
from werkzeug.datastructures import FileStorage
from sentence_transformers import SentenceTransformer
import torch
# from fast_sentence_transformers import FastSentenceTransformer as SentenceTransformer # https://www.philschmid.de/optimize-sentence-transformers
import pymupdf4llm
from . import vector_db


# Keep the model in memory to avoid reloading it every time (For performance)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2", device="cuda", model_kwargs={
    "torch_dtype": torch.float16,
})

db = vector_db.VectorDB()


def process_document(conversation_id: int, document: FileStorage):
    """
    Process the document to extract relevant information.
    """
    # Create a collection for the conversation
    db.create_collection(conversation_id, dimension=384) # 384 for all-MiniLM-L6-v2

    # Embedding
    fragments = __divide_document_into_fragments(document)
    print("Document split into fragments, now embedding...")
    data = __get_embeddings_with_texts(fragments)
    print("Document embedded!")

    # Insert data into the vector database
    db.insert_data(conversation_id, data)


def __divide_document_into_fragments(document: FileStorage):
    """
    Divide the document into fragments for embedding.
    :param document: FileStorage
    :return: list of fragments
    """
    document = Document(stream = document.read(), filetype="pdf")
    print("Document loaded, parsing to markdown...")
    parsed_document_to_markdown = pymupdf4llm.to_markdown(doc = document)
    print("Document parsed to markdown, now splitting into fragments...")

    # Split the document into fragments
    fragments = split_fixed_chunks(parsed_document_to_markdown)
    print("Document split into fragments!")

    return fragments


def split_fixed_chunks(text, chunk_size=256):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def __get_embeddings_with_texts(fragments: list):
    """
    Get embeddings for the fragments.
    :param fragments: list of fragments
    :return: list of embeddings
    """
    embeddings = []

    for fragment in fragments:
        embedding = model.encode(fragment)
        embeddings.append({
            "text": fragment,
            "embedding": embedding.tolist()
        })

    return embeddings


def can_process_query(conversation_id: int):
    if not db.has_collection(conversation_id):
        return False
    return True


def process_query(conversation_id: int, query: str) -> list:
    """
    Process the query to extract relevant information. Returns the most relevant document.
    """
    # Embedding
    print("Embedding query...")
    query_embedding = [__get_embeddings_with_texts([query])[0]['embedding']]
    print("Query embedded, now searching...")

    # Search the vector database
    results = db.search(conversation_id, query_embedding)
    print("Search completed, now reranking...")
    result = db.rerank(results, query)
    print("Reranking completed!")

    return result