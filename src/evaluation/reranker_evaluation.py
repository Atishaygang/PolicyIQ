import json
import time
from pathlib import Path

from src.retrieval.hybrid_retriever import hybrid_search
from src.retrieval.reranker import rerank_documents


QUESTIONS_PATH = Path(
    "evaluation/questions.json"
)


def load_questions():

    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data["questions"]


def normalize_pages(page_value):

    if isinstance(
        page_value,
        list
    ):
        return page_value

    return [page_value]


def get_expected_pairs(question):

    expected_pairs = set()

    for evidence in question[
        "expected_evidence"
    ]:

        document_id = evidence[
            "document_id"
        ]

        pages = normalize_pages(
            evidence["page"]
        )

        for page in pages:

            expected_pairs.add(
                (
                    document_id,
                    page
                )
            )

    return expected_pairs


def get_retrieved_pairs(
    documents
):

    return [
        (
            doc.metadata[
                "document_id"
            ],
            doc.metadata[
                "pdf_page"
            ]
        )
        for doc in documents
    ]


def evaluate_question(
    question
):

    start = time.perf_counter()

    # ==========================================
    # Exact same runtime retrieval path
    # ==========================================

    hybrid_documents = hybrid_search(
        query=question["question"],
        dense_k=10,
        bm25_k=10,
        final_k=10
    )

    documents = rerank_documents(
        query=question["question"],
        documents=hybrid_documents,
        top_n=5
    )

    end = time.perf_counter()

    expected_pairs = (
        get_expected_pairs(
            question
        )
    )

    retrieved_pairs = (
        get_retrieved_pairs(
            documents
        )
    )

    hit_ranks = []

    for rank, pair in enumerate(
        retrieved_pairs,
        start=1
    ):

        if pair in expected_pairs:
            hit_ranks.append(
                rank
            )

    first_hit_rank = (
        min(hit_ranks)
        if hit_ranks
        else None
    )

    return {
        "question_id":
            question["question_id"],

        "category":
            question["category"],

        "question":
            question["question"],

        "expected_pairs":
            list(expected_pairs),

        "retrieved_pairs":
            retrieved_pairs,

        "first_hit_rank":
            first_hit_rank,

        "latency_seconds":
            end - start
    }


def calculate_hit_at_k(
    results,
    k
):

    hits = 0

    for result in results:

        rank = result[
            "first_hit_rank"
        ]

        if (
            rank is not None
            and rank <= k
        ):
            hits += 1

    total = len(results)

    percentage = (
        hits / total * 100
        if total > 0
        else 0
    )

    return {
        "hits": hits,
        "total": total,
        "percentage": percentage
    }


def main():

    questions = load_questions()

    answerable_questions = [
        question
        for question in questions
        if question["answerable"]
    ]

    results = []

    print(
        "\n=============================="
    )
    print(
        "POLICYIQ FP32 RERANKER EVAL"
    )
    print(
        "=============================="
    )

    for question in answerable_questions:

        result = evaluate_question(
            question
        )

        results.append(
            result
        )

        print(
            f"\n{result['question_id']}"
        )

        print(
            "First Hit Rank:",
            result[
                "first_hit_rank"
            ]
        )

        print(
            "Latency:",
            f"{result['latency_seconds']:.2f}s"
        )


    print(
        "\n=============================="
    )
    print(
        "FP32 RETRIEVAL RESULTS"
    )
    print(
        "=============================="
    )

    for k in [1, 3, 5]:

        metric = calculate_hit_at_k(
            results,
            k
        )

        print(
            f"Hit@{k}: "
            f"{metric['hits']}/"
            f"{metric['total']} "
            f"= "
            f"{metric['percentage']:.1f}%"
        )


    average_latency = (
        sum(
            result[
                "latency_seconds"
            ]
            for result in results
        )
        / len(results)
    )

    print(
        "\nAverage retrieval + "
        "reranking latency:"
    )

    print(
        f"{average_latency:.2f}s"
    )


if __name__ == "__main__":
    main()