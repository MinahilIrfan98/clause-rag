#from langchain_core.documents import Document
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import Distance, VectorParams


from app.core.config import get_settings, get_embeddings, get_qdrant_client
def load(path: str):
    return PyPDFLoader(path).load()
    

def ingest():
    settings = get_settings()

    #load
    file = load(settings.data_path)

    #2. chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(file)

    #embeddings
    embed = get_embeddings(settings)

    #4. store
    client = get_qdrant_client(settings)

    try:
        if client.collection_exists(collection_name=settings.collection):
            client.delete_collection(collection_name=settings.collection)  # prev table should be deleted before creating new one so that chunks do not duplicate
        client.create_collection(
            collection_name=settings.collection,
            vectors_config=VectorParams(
                size=settings.embed_dim,
                distance=Distance.COSINE
            )
        )

        vector_store = QdrantVectorStore(
            client=client,
            collection_name=settings.collection,
            embedding=embed
        )
        vector_store.add_documents(chunks)
    finally:
        client.close()

    return len(chunks)