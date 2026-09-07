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

    end = time.perf_counter()

    timings["hybrid_retrieval_ms"] = (
        end - start
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
    print("\n==============================")
    print("RERANKED EVIDENCE DEBUG")
    print("==============================")

    for index, doc in enumerate(
        documents,
        start=1
    ):
        print(
        f"\nRANK {index}"
        )

        print(
        f"{doc.metadata['document_id']} "
        f"| Page {doc.metadata['pdf_page']}"
        )

        print(
        doc.page_content[:500]
        )

        print(
        "-" * 60
        )

    end = time.perf_counter()

    timings["reranking_ms"] = (
        end - start
    ) * 1000


    # ==========================================
    # Step 3:
    # Build context + prompt
    # ==========================================

    start = time.perf_counter()

    context = build_context(
        documents
    )

    formatted_user_prompt = USER_PROMPT.format(
        context=context,
        question=question
    )

    end = time.perf_counter()

    timings["context_prompt_ms"] = (
        end - start
    ) * 1000


    # ==========================================
    # Step 4:
    # Get LLM client
    # ==========================================

    start = time.perf_counter()

    llm = get_llm()

    end = time.perf_counter()

    timings["llm_client_ms"] = (
        end - start
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

    end = time.perf_counter()

    timings["llm_generation_ms"] = (
        end - start
    ) * 1000


    # ==========================================
    # Step 6:
    # Build final response
    # ==========================================

    start = time.perf_counter()

    sources = build_sources(
        documents
    )

    end = time.perf_counter()

    timings["response_build_ms"] = (
        end - start
    ) * 1000


    total_end = time.perf_counter()

    timings["total_ms"] = (
        total_end - total_start
    ) * 1000


    result = {
        "question": question,
        "answer": response.content,
        "sources": sources,
        "retrieved_documents": documents,
        "timings": timings
    }

    return result


def warm_local_components(question):

    print(
        "\n=============================="
    )
    print(
        "WARMING LOCAL COMPONENTS"
    )
    print(
        "=============================="
    )

    hybrid_documents = hybrid_search(
        query=question,
        dense_k=10,
        bm25_k=10,
        final_k=10
    )

    rerank_documents(
        query=question,
        documents=hybrid_documents,
        top_n=5
    )

    get_llm()

    print(
        "Local warm-up complete."
    )


if __name__ == "__main__":

    question = (
        "What percentage depreciation applies to rubber, nylon, "
        "plastic parts, tyres, tubes, batteries and air bags under "
        "the standalone private car own-damage policy?"
    )

    # Warm cached local components first.
    #
    # This prevents model loading / BM25 construction /
    # vector-store initialization from contaminating the
    # steady-state query latency measurement.

    warm_local_components(
        question
    )


    print(
        "\n=============================="
    )
    print(
        "RUNNING PROFILED QUERY"
    )
    print(
        "=============================="
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
        "PIPELINE LATENCY PROFILE"
    )
    print(
        "=============================="
    )

    timings = result[
        "timings"
    ]

    total_ms = timings[
        "total_ms"
    ]

    labels = {
        "hybrid_retrieval_ms":
            "Hybrid retrieval",

        "reranking_ms":
            "Jina reranking",

        "context_prompt_ms":
            "Context + prompt",

        "llm_client_ms":
            "LLM client",

        "llm_generation_ms":
            "LLM generation",

        "response_build_ms":
            "Response build"
    }

    for key, label in labels.items():

        value = timings[
            key
        ]

        percentage = (
            value
            / total_ms
            * 100
        )

        print(
            f"{label:<20}"
            f"{value / 1000:>8.2f} s"
            f"   "
            f"{percentage:>6.2f}%"
        )


    print(
        "------------------------------"
    )

    print(
        f"{'TOTAL':<20}"
        f"{total_ms / 1000:>8.2f} s"
    )