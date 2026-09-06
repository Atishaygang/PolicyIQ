from src.retrieval.retriever import retrieve_documents
from src.retrieval.bm_25_retriever import bm25_search


def reciprocal_rank_fusion(
    dense_results,
    bm25_results,
    k=60,
    top_n=5
):
    scores = {}
    documents = {}

    # Dense results
    for rank, doc in enumerate(dense_results, start=1):

        chunk_key = (
            doc.metadata["document_id"],
            doc.metadata["pdf_page"],
            doc.page_content
        )

        scores[chunk_key] = (
            scores.get(chunk_key, 0)
            + 1 / (k + rank)
        )

        documents[chunk_key] = doc

    # BM25 results
    for rank, doc in enumerate(bm25_results, start=1):

        chunk_key = (
            doc.metadata["document_id"],
            doc.metadata["pdf_page"],
            doc.page_content
        )

        scores[chunk_key] = (
            scores.get(chunk_key, 0)
            + 1 / (k + rank)
        )

        documents[chunk_key] = doc

    # Rank chunks
    ranked_keys = sorted(
        scores,
        key=scores.get,
        reverse=True
    )

    # Page-level deduplication AFTER ranking
    fused_results = []
    seen_pages = set()

    for key in ranked_keys:

        doc = documents[key]

        page_key = (
            doc.metadata["document_id"],
            doc.metadata["pdf_page"]
        )

        if page_key in seen_pages:
            continue

        seen_pages.add(page_key)
        fused_results.append(doc)

        if len(fused_results) == top_n:
            break

    return fused_results


def hybrid_search(
    query,
    dense_k=20,
    bm25_k=20,
    final_k=5
):
    dense_results = retrieve_documents(
        query=query,
        k=dense_k
    )

    bm25_results = bm25_search(
        query=query,
        k=bm25_k
    )

    results = reciprocal_rank_fusion(
        dense_results=dense_results,
        bm25_results=bm25_results,
        top_n=final_k
    )

    return results


if __name__ == "__main__":

    query = "What is No Claim Bonus?"

    results = hybrid_search(
        query=query,
        dense_k=20,
        bm25_k=20,
        final_k=5
    )

    for index, doc in enumerate(results, start=1):

        print(
            index,
            doc.metadata["document_id"],
            doc.metadata["pdf_page"],
            doc.page_content[:200]
        )