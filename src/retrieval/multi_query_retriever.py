from src.retrieval.query_rewriter import generate_queries
from src.retrieval.hybrid_retriever import hybrid_search


def multi_query_search(
    question,
    per_query_k=20,
    final_k=20,
    rrf_k=60
):
    queries = generate_queries(question)

    scores = {}
    documents = {}

    for query in queries:

        results = hybrid_search(
            query=query,
            dense_k=20,
            bm25_k=20,
            final_k=per_query_k
        )

        for rank, doc in enumerate(results, start=1):

            chunk_key = (
                doc.metadata["document_id"],
                doc.metadata["pdf_page"],
                doc.page_content
            )

            scores[chunk_key] = (
                scores.get(chunk_key, 0)
                + 1 / (rrf_k + rank)
            )

            documents[chunk_key] = doc

    ranked_keys = sorted(
        scores,
        key=scores.get,
        reverse=True
    )

    final_results = []
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
        final_results.append(doc)

        if len(final_results) == final_k:
            break

    return final_results


if __name__ == "__main__":

    question = "Will my insurance pay if the driver was drunk?"

    results = multi_query_search(
        question=question,
        per_query_k=20,
        final_k=20
    )

    for index, doc in enumerate(results, start=1):
        print(
            index,
            doc.metadata["document_id"],
            doc.metadata["pdf_page"],
            doc.page_content[:200]
        )