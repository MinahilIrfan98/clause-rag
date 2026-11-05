from pathlib import Path

from langchain.chat_models import init_chat_model  # LLM
from langchain.embeddings import init_embeddings  # Embeddings
from langchain_core.documents import Document  # .md, .csv
# from langchain_community.document_loaders import PyPDFLoader  # .pdf
from langchain_text_splitters import RecursiveCharacterTextSplitter  # chunks
from langchain_core.vectorstores import InMemoryVectorStore  # vector store

# Indexing
# 1. Load
DATA_DIR = Path(__file__).resolve().parent.parent / "data"  # api/data
text = (DATA_DIR / "shop_handbook.md").read_text(encoding="utf-8")  # string object
print(text[:300])  # pehle 300 characters dekhne ke liye

# 2. Chunk
splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
chunks = splitter.split_text(text)
print(len(chunks))  # kitne chunks bane
print(chunks[0])    # pehla chunk