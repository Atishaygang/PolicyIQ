from src.retrieval.embeddings import get_embed_model
from src.ingestion.corpus import load_corpus
from src.chunking.splitter import split_documents
from langchain_chroma import Chroma
import json

with open(
    r"evaluation/questions.json",
    'r',
    encoding='utf-8'
) as file:
    questions = json.load(file)




def load_vector_store():
    embedding_model = get_embed_model()
    vector_store = Chroma(
        collection_name="policyiq_v1",
        persist_directory=r"D:\Policy_IQ\data\processed",
        embedding_function = embedding_model
    )
    return vector_store

