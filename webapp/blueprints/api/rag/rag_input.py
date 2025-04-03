from werkzeug.datastructures import FileStorage
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pymupdf4llm
from . import vector_db


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
            "vector": embedding.tolist()
        })

    # Insert data into the vector database
    db.insert_data(collection_name, data)



def __divide_document_into_fragments(document: FileStorage):
    """
    Divide the document into fragments for embedding.
    :param document: FileStorage
    :return: list of fragments
    """
    parsed_document_to_markdown = pymupdf4llm.to_markdown(document)

    # Split the document into fragments
    splitter = RecursiveCharacterTextSplitter(chunk_size=400)
    fragments = splitter.split_text(parsed_document_to_markdown)

    return fragments