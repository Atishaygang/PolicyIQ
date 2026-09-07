from functools import lru_cache
from langchain_chroma import Chroma

from src.retrieval.embeddings import get_embed_model


PERSIST_DIRECTORY = r"D:\Policy_IQ\data\processed"


@lru_cache(maxsize=1)
def load_vector_store():

    vector_store = Chroma(
        collection_name="policyiq_v1",
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=get_embed_model()
    )

    return vector_store


if __name__ == "__main__":

    vector_store = load_vector_store()

    docs = vector_store.similarity_search(
        "What about health insurance",
        k=5
    )

    for i, doc in enumerate(
        docs,
        start=1
    ):
        print(
            f"\n--- CHUNK {i} ---"
        )

        print(
            doc.metadata["category"]
        )