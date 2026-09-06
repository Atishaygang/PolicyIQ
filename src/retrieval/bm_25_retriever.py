from functools import lru_cache
from rank_bm25 import BM25Okapi

from src.ingestion.corpus import load_corpus
from src.chunking.splitter import split_documents


@lru_cache(maxsize=1)
def build_bm25():

    documents = load_corpus(
        data_dir=r"D:\Policy_IQ\data\raw",
        manifest_path=r"D:\Policy_IQ\data\menifest.csv"
    )

    chunks = split_documents(
        documents,
        chunk_size=1200,
        chunk_overlap=200
    )

    tokenized_corpus = [
        chunk.page_content.lower().split()
        for chunk in chunks
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    return chunks, bm25


def bm25_search(query, k=5):

    chunks, bm25 = build_bm25()

    tokenized_query = query.lower().split()

    scores = bm25.get_scores(tokenized_query)

    ranked_indices = scores.argsort()[::-1][:k]

    results = [
        chunks[i]
        for i in ranked_indices
    ]

    return results


if __name__ == "__main__":

    query = "What is No Claim Bonus?"

    results = bm25_search(query, k=5)

    for index, doc in enumerate(results, start=1):

        print(
            index,
            doc.metadata["document_id"],
            doc.metadata["pdf_page"],
            doc.page_content[:200]
        )