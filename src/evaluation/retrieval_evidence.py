from src.retrieval.query_vector_store import load_vector_store

import json


def hit_at_k(expected_pair, retrieved_pair, k):

    top_k_pairs = retrieved_pair[:k]

    hit = any(
        pair in top_k_pairs
        for pair in expected_pair
    )

    if hit:
        return 1
    else:
        return 0


with open(
    r"evaluation/questions.json",
    "r",
    encoding="utf-8"
) as file:

    questions = json.load(file)


vector_store = load_vector_store()


for question in questions["questions"]:

    if question["category"] == "unanswerable":
        continue

    query = question["question"]

    results = vector_store.similarity_search(
        query,
        k=20
    )

    top_1 = results[:1]
    top_3 = results[:3]
    top_5 = results[:5]
    top_10 = results[:10]
    top_15 = results[:15]
    top_20 = results[:20]


    # -----------------------------
    # Print ranked retrieval
    # -----------------------------

    for rank, doc in enumerate(
        top_20,
        start=1
    ):

        print(
            rank,
            "\n ---Question-Id---",
            question["question_id"],
            doc.metadata["document_id"],
            doc.metadata["pdf_page"]
        )


    # -----------------------------
    # Build expected evidence pairs
    # -----------------------------

    expected_pair = set()

    for evidence in question["expected_evidence"]:

        document_id = evidence["document_id"]
        pages = evidence["page"]

        if isinstance(pages, int):
            pages = [pages]

        for page in pages:

            expected_pair.add(
                (
                    document_id,
                    page
                )
            )


    print(
        "\n ---Expected_pair---",
        expected_pair
    )


    # -----------------------------
    # Build retrieved pairs
    # -----------------------------

    retrieved_pair = []

    for doc in top_20:

        retrieved_pair.append(
            (
                doc.metadata["document_id"],
                doc.metadata["pdf_page"]
            )
        )


    print(
        "\n---retrieved_pair---",
        retrieved_pair
    )


    # -----------------------------
    # Hit@K
    # -----------------------------

    print(
        "Hit@1:",
        hit_at_k(
            expected_pair,
            retrieved_pair,
            1
        )
    )

    print(
        "Hit@3:",
        hit_at_k(
            expected_pair,
            retrieved_pair,
            3
        )
    )

    print(
        "Hit@5:",
        hit_at_k(
            expected_pair,
            retrieved_pair,
            5
        )
    )

    print(
        "Hit@10:",
        hit_at_k(
            expected_pair,
            retrieved_pair,
            10
        )
    )

    print(
        "Hit@15:",
        hit_at_k(
            expected_pair,
            retrieved_pair,
            15
        )
    )

    print(
        "Hit@20:",
        hit_at_k(
            expected_pair,
            retrieved_pair,
            20
        )
    )