import json
from pathlib import Path

from src.retrieval.reranker import query_expanded_reranked_search


QUESTIONS_PATH = Path("evaluation/questions.json")


def load_questions():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["questions"]


def normalize_pages(page_value):
    if isinstance(page_value, list):
        return page_value

    return [page_value]


def get_expected_pairs(question):
    expected_pairs = set()

    for evidence in question["expected_evidence"]:
        document_id = evidence["document_id"]

        pages = normalize_pages(evidence["page"])

        for page in pages:
            expected_pairs.add(
                (
                    document_id,
                    page
                )
            )

    return expected_pairs


def get_retrieved_pairs(documents):
    return [
        (
            doc.metadata["document_id"],
            doc.metadata["pdf_page"]
        )
        for doc in documents
    ]


def evaluate_question(question):
    retrieved_documents = query_expanded_reranked_search(
        query=question["question"],
        candidate_k=5,
        final_k=5
    )

    expected_pairs = get_expected_pairs(question)

    retrieved_pairs = get_retrieved_pairs(
        retrieved_documents
    )

    hit_ranks = []

    for rank, pair in enumerate(
        retrieved_pairs,
        start=1
    ):
        if pair in expected_pairs:
            hit_ranks.append(rank)

    first_hit_rank = (
        min(hit_ranks)
        if hit_ranks
        else None
    )

    return {
        "question_id": question["question_id"],
        "category": question["category"],
        "question": question["question"],
        "expected_pairs": list(expected_pairs),
        "retrieved_pairs": retrieved_pairs,
        "first_hit_rank": first_hit_rank
    }


def calculate_hit_at_k(results, k):
    hits = 0

    for result in results:
        rank = result["first_hit_rank"]

        if rank is not None and rank <= k:
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

    for question in answerable_questions:
        result = evaluate_question(question)

        results.append(result)

        print("\n==============================")
        print(result["question_id"])
        print("==============================")

        print(
            "Expected:",
            result["expected_pairs"]
        )

        print(
            "Retrieved:",
            result["retrieved_pairs"]
        )

        print(
            "First Hit Rank:",
            result["first_hit_rank"]
        )

    print("\n==============================")
    print("QUERY EXPANSION + HYBRID + RERANKER RESULTS")
    print("==============================")

    for k in [1, 3, 5]:
        metric = calculate_hit_at_k(
            results,
            k
        )

        print(
            f"Hit@{k}: "
            f"{metric['hits']}/"
            f"{metric['total']} "
            f"= {metric['percentage']:.1f}%"
        )


if __name__ == "__main__":
    main()