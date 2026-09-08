import time

from src.retrieval.hybrid_retriever import hybrid_search
from src.retrieval.reranker import rerank_documents

from src.rag.llm import get_llm
from src.rag.prompt import SYSTEM_PROMPT, USER_PROMPT


def build_context(documents):

    context_parts = []

    for index, doc in enumerate(
        documents,
        start=1
    ):
        source = (
            f"[SOURCE {index}]\n"
            f"Document ID: {doc.metadata['document_id']}\n"
            f"Filename: {doc.metadata['filename']}\n"
            f"PDF Page: {doc.metadata['pdf_page']}\n"
            f"Content:\n"
            f"{doc.page_content}"
        )

        context_parts.append(source)

    return "\n\n".join(context_parts)


def build_sources(documents):

    sources = []

    for doc in documents:

        source = {
            "document_id": doc.metadata["document_id"],
            "filename": doc.metadata["filename"],
            "page": doc.metadata["pdf_page"]
        }

        sources.append(source)

    return sources


def ask_policyiq(question):

    total_start = time.perf_counter()

    timings = {}


    # ==========================================
    # Step 1:
    # Dense + BM25 -> RRF -> Hybrid Top 10
    # ==========================================

    start = time.perf_counter()

    hybrid_documents = hybrid_search(
        query=question,
        dense_k=10,
        bm25_k=10,
        final_k=10
    )

    timings["hybrid_retrieval_ms"] = (
        time.perf_counter() - start
    ) * 1000


    # ==========================================
    # Step 2:
    # Jina reranker -> Final Top 5
    # ==========================================

    start = time.perf_counter()

    documents = rerank_documents(
        query=question,
        documents=hybrid_documents,
        top_n=5
    )

    timings["reranking_ms"] = (
        time.perf_counter() - start
    ) * 1000


    # ==========================================
    # Step 3:
    # Build grounded context + prompt
    # ==========================================

    start = time.perf_counter()

    context = build_context(
        documents
    )

    formatted_user_prompt = USER_PROMPT.format(
        context=context,
        question=question
    )

    timings["context_prompt_ms"] = (
        time.perf_counter() - start
    ) * 1000


    # ==========================================
    # Step 4:
    # Get cached LLM client
    # ==========================================

    start = time.perf_counter()

    llm = get_llm()

    timings["llm_client_ms"] = (
        time.perf_counter() - start
    ) * 1000


    # ==========================================
    # Step 5:
    # Generate grounded answer
    # ==========================================

    start = time.perf_counter()

    response = llm.invoke(
        [
            (
                "system",
                SYSTEM_PROMPT
            ),
            (
                "human",
                formatted_user_prompt
            )
        ]
    )

    timings["llm_generation_ms"] = (
        time.perf_counter() - start
    ) * 1000


    # ==========================================
    # Step 6:
    # Build final source response
    # ==========================================

    start = time.perf_counter()

    sources = build_sources(
        documents
    )

    timings["response_build_ms"] = (
        time.perf_counter() - start
    ) * 1000


    # ==========================================
    # Total end-to-end latency
    # ==========================================

    timings["total_ms"] = (
        time.perf_counter() - total_start
    ) * 1000


    result = {
        "question": question,
        "answer": response.content,
        "sources": sources,
        "retrieved_documents": documents,
        "timings": timings
    }

    return result


if __name__ == "__main__":

    question = (
        "What percentage depreciation applies to rubber, nylon, "
        "plastic parts, tyres, tubes, batteries and air bags under "
        "the standalone private car own-damage policy?"
    )

    result = ask_policyiq(
        question
    )


    print(
        "\n=============================="
    )
    print(
        "POLICYIQ ANSWER"
    )
    print(
        "=============================="
    )

    print(
        result["answer"]
    )


    print(
        "\n=============================="
    )
    print(
        "RETRIEVED SOURCES"
    )
    print(
        "=============================="
    )

    for index, source in enumerate(
        result["sources"],
        start=1
    ):

        print(
            f"{index}. "
            f"{source['document_id']} "
            f"| {source['filename']} "
            f"| Page {source['page']}"
        )


    print(
        "\n=============================="
    )
    print(
        "PIPELINE LATENCY"
    )
    print(
        "=============================="
    )

    timings = result[
        "timings"
    ]

    print(
        f"Hybrid retrieval: "
        f"{timings['hybrid_retrieval_ms'] / 1000:.2f}s"
    )

    print(
        f"Jina reranking: "
        f"{timings['reranking_ms'] / 1000:.2f}s"
    )

    print(
        f"Context + prompt: "
        f"{timings['context_prompt_ms'] / 1000:.4f}s"
    )

    print(
        f"LLM client: "
        f"{timings['llm_client_ms'] / 1000:.4f}s"
    )

    print(
        f"LLM generation: "
        f"{timings['llm_generation_ms'] / 1000:.2f}s"
    )

    print(
        f"Response build: "
        f"{timings['response_build_ms'] / 1000:.4f}s"
    )

    print(
        "------------------------------"
    )

    print(
        f"TOTAL: "
        f"{timings['total_ms'] / 1000:.2f}s"
    )