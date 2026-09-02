from src.retrieval.embeddings import get_embed_model
from src.ingestion.corpus import load_corpus
from src.chunking.splitter import split_documents
from langchain_chroma import Chroma


def build_vector_store():
    corpus = load_corpus(
        data_dir= r'D:\Policy_IQ\data\raw',
        manifest_path=r'D:\Policy_IQ\data\menifest.csv'
    )
    chunks = split_documents(
        documents=corpus
    )
    embedding_model = get_embed_model(
    )
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding= embedding_model,
        collection_name="policyiq_v1",
        persist_directory= 'D:\Policy_IQ\data\processed'
    )
    return vector_store