from pymupdf import Document
from fastapi import UploadFile
from sentence_transformers import SentenceTransformer
import torch
from multiprocessing import Pool, cpu_count
# from fast_sentence_transformers import FastSentenceTransformer as SentenceTransformer # https://www.philschmid.de/optimize-sentence-transformers
import pymupdf4llm
import os

from api import db


# https://github.com/huggingface/transformers/issues/5486
os.environ["TOKENIZERS_PARALLELISM"] = "true"  # Explicty set Parallelism in tokenizers to avoid issues with multiprocessing


# Keep the model in memory to avoid reloading it every time (For performance)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2", device=device, model_kwargs={
    "torch_dtype": torch.float16,
})



def process_document(conversation_id: int, document: UploadFile):
    """
    Process the document to extract relevant information.
    """
    # Create a collection for the conversation
    if not db.has_collection(conversation_id):
        db.create_collection(conversation_id, dimension=384) # 384 for all-MiniLM-L6-v2

    # Embedding
    fragments = __divide_document_into_fragments(document)
    print("Document split into fragments, now embedding...")
    data = __get_embeddings_with_texts(fragments)
    print("Document embedded!")

    # Insert data into the vector database
    db.insert_data(conversation_id, data)


def __divide_document_into_fragments(document: UploadFile):
    """
    Divide the document into fragments for embedding. Use multiprocessing to speed up the process.
    """
    num_proc = cpu_count()
    pdf_bytes = document.read()
    doc = Document(stream=pdf_bytes, filetype="pdf")
    total_pages = doc.page_count

    # Divide the pages into chunks for each process
    pages_list = []
    pages = list(range(total_pages))
    chunk_size = (total_pages + num_proc - 1) // num_proc

    for i in range(0, total_pages, chunk_size):
        pages_list.append(pages[i:i + chunk_size])

    # Use multiprocessing to parse the document
    print("Parsing document to markdown...")
    with Pool(processes=num_proc) as pool:
        results = pool.starmap(__parse_to_markdown, [(pdf_bytes, pages) for pages in pages_list])
        parsed_document_to_markdown = "".join(results)
    print("Document parsed to markdown!")

    # Split the document into fragments
    print("Splitting document into fragments...")
    fragments = split_fixed_chunks(parsed_document_to_markdown)
    print("Document split into fragments!")

    return fragments


def __parse_to_markdown(pdf_bytes: bytes, pages: list):
    """
    Parse given pages of the document to markdown.
    """
    doc = Document(stream=pdf_bytes, filetype="pdf")
    return pymupdf4llm.to_markdown(doc=doc, pages=pages)


def split_fixed_chunks(text, chunk_size=256):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def __get_embeddings_with_texts(fragments: list):
    """
    Get embeddings for the fragments (batched).
    """
    embeddings_array = model.encode(fragments, show_progress_bar=True)

    return [
        {
            "text": fragment,
            "embedding": embedding.tolist()
        }
        for fragment, embedding in zip(fragments, embeddings_array)
    ]


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
