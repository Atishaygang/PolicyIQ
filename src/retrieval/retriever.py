from src.retrieval.query_vector_store import load_vector_store


def retrieve_documents(
        query,
        k=5,
        metadata_filter = None
        ):
    vector_store = load_vector_store()
    if metadata_filter:
        documents = vector_store.similarity_search(
            query,
            k =k,
            filter = metadata_filter
            )
    else:
        documents = vector_store.similarity_search(
            query,
            k= k
            )
    return documents

    

    