from src.retrieval.query_vector_store import load_vector_store


def retrieve_documents(query, k=5):

    vector_store = load_vector_store()

    documents = vector_store.similarity_search(
        query,
        k=k
    )

    return documents