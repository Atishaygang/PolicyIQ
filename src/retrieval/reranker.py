from functools import lru_cache

from transformers import AutoModel

from src.retrieval.multi_query_retriever import multi_query_search


MODEL_NAME = "jinaai/jina-reranker-v3"


@lru_cache(maxsize=1)
def get_reranker():
    model = AutoModel.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        dtype="auto"
    )

    model.eval()

    return model


def rerank_documents(
    query,
    documents,
    top_n=5
):
    model = get_reranker()

    document_texts = [
        doc.page_content
        for doc in documents
    ]

    ranked_results = model.rerank(
        query,
        document_texts,
        top_n=top_n
    )

    reranked_documents = [
        documents[result["index"]]
        for result in ranked_results
    ]

    return reranked_documents


def query_expanded_reranked_search(
    query,
    candidate_k=5,
    final_k=5
):
    candidates = multi_query_search(
        question=query,
        per_query_k=5,
        final_k=candidate_k
    )

    results = rerank_documents(
        query=query,
        documents=candidates,
        top_n=final_k
    )

    return results


if __name__ == "__main__":
    query = "Will my insurance pay if the driver was drunk?"

    results = query_expanded_reranked_search(
        query=query,
        candidate_k=5,
        final_k=5
    )

    for index, doc in enumerate(results, start=1):
        print(
            index,
            doc.metadata["document_id"],
            doc.metadata["pdf_page"],
            doc.page_content[:200]
        )