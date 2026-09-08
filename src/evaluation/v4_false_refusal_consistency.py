import json
import time
import hashlib
from pathlib import Path

from src.retrieval.hybrid_retriever import hybrid_search
from src.retrieval.reranker import rerank_documents

from src.rag.llm import get_llm
from src.rag.prompt import SYSTEM_PROMPT, USER_PROMPT
from src.rag.pipeline import build_context


QUESTIONS_PATH = Path(
    "evaluation/questions.json"
)

NUMBER_OF_RUNS = 5

REFUSAL_TEXT = (
    "I could not find sufficient information "
    "in the provided documents."
)


def load_questions():

    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data["questions"]


def main():

    questions = load_questions()

    q008 = next(
        question
        for question in questions
        if question["question_id"] == "Q008"
    )

    question = q008["question"]


    print(
        "\n======================================"
    )
    print(
        "V4 FALSE-REFUSAL CONSISTENCY TEST"
    )
    print(
        "======================================"
    )

    print(
        "\nQuestion:"
    )

    print(
        question
    )


    # ==========================================
    # Retrieve ONCE
    # ==========================================

    print(
        "\nRetrieving evidence once..."
    )

    hybrid_documents = hybrid_search(
        query=question,
        dense_k=10,
        bm25_k=10,
        final_k=10
    )


    # ==========================================
    # Rerank ONCE
    # ==========================================

    documents = rerank_documents(
        query=question,
        documents=hybrid_documents,
        top_n=5
    )


    print(
        "\nFinal frozen evidence:"
    )

    for index, doc in enumerate(
        documents,
        start=1
    ):

        print(
            f"{index}. "
            f"{doc.metadata['document_id']} "
            f"| Page "
            f"{doc.metadata['pdf_page']}"
        )


    # ==========================================
    # Freeze exact context
    # ==========================================

    context = build_context(
        documents
    )

    context_hash = hashlib.sha256(
        context.encode(
            "utf-8"
        )
    ).hexdigest()


    print(
        "\nContext SHA256:"
    )

    print(
        context_hash
    )


    formatted_user_prompt = USER_PROMPT.format(
        context=context,
        question=question
    )


    # ==========================================
    # Load LLM once
    # ==========================================

    llm = get_llm()


    # ==========================================
    # Generate 5 times with IDENTICAL context
    # ==========================================

    results = []

    for run_number in range(
        1,
        NUMBER_OF_RUNS + 1
    ):

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

        latency = (
            time.perf_counter()
            - start
        )


        answer = (
            response.content.strip()
        )


        refused = (
            REFUSAL_TEXT.lower()
            in answer.lower()
        )


        results.append(
            {
                "run": run_number,
                "refused": refused,
                "latency": latency,
                "answer": answer
            }
        )


        print(
            "\n======================================"
        )

        print(
            f"RUN {run_number}"
        )

        print(
            "======================================"
        )

        print(
            "Refused:",
            refused
        )

        print(
            f"Generation latency: "
            f"{latency:.2f}s"
        )

        print(
            "\nAnswer:"
        )

        print(
            answer
        )


    # ==========================================
    # Summary
    # ==========================================

    refusal_count = sum(
        1
        for result in results
        if result["refused"]
    )

    answer_count = (
        NUMBER_OF_RUNS
        - refusal_count
    )


    print(
        "\n\n======================================"
    )
    print(
        "CONSISTENCY SUMMARY"
    )
    print(
        "======================================"
    )

    print(
        "Total runs:",
        NUMBER_OF_RUNS
    )

    print(
        "Refusals:",
        refusal_count
    )

    print(
        "Non-refusals:",
        answer_count
    )


    if (
        refusal_count > 0
        and answer_count > 0
    ):

        print(
            "\nResult:"
        )

        print(
            "GENERATION INCONSISTENCY DETECTED"
        )

        print(
            "The same frozen evidence produced "
            "both refusal and non-refusal answers."
        )


    elif refusal_count == NUMBER_OF_RUNS:

        print(
            "\nResult:"
        )

        print(
            "CONSISTENT FALSE-REFUSAL BEHAVIOR"
        )

        print(
            "The generation layer consistently "
            "refused using the same evidence."
        )


    else:

        print(
            "\nResult:"
        )

        print(
            "CONSISTENT NON-REFUSAL BEHAVIOR"
        )

        print(
            "No false refusal occurred across "
            "the five identical-context runs."
        )


if __name__ == "__main__":
    main()