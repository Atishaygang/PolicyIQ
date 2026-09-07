import json
import time
from pathlib import Path

from src.rag.pipeline import ask_policyiq


QUESTIONS_PATH = Path("evaluation/questions.json")

OUTPUT_DIR = Path("evaluation/rag_runs")
OUTPUT_PATH = OUTPUT_DIR / "v3_baseline.json"


def load_questions():
    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    return data["questions"]


def load_existing_results():

    if not OUTPUT_PATH.exists():
        return []

    with open(
        OUTPUT_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    return data.get(
        "results",
        []
    )


def serialize_retrieved_documents(documents):

    retrieved = []

    for rank, doc in enumerate(
        documents,
        start=1
    ):

        retrieved.append(
            {
                "rank": rank,

                "chunk_id": doc.metadata.get(
                    "chunk_id"
                ),

                "document_id": doc.metadata.get(
                    "document_id"
                ),

                "filename": doc.metadata.get(
                    "filename"
                ),

                "page": doc.metadata.get(
                    "pdf_page"
                ),

                "content": doc.page_content
            }
        )

    return retrieved


def evaluate_question(question):

    start = time.perf_counter()

    result = ask_policyiq(
        question["question"]
    )

    end = time.perf_counter()

    latency_ms = (
        end - start
    ) * 1000

    retrieved = serialize_retrieved_documents(
        result["retrieved_documents"]
    )

    trace = {
        "question_id": question["question_id"],

        "question": question["question"],

        "category": question["category"],

        "answerable": question["answerable"],

        "generated_answer": result["answer"],

        "retrieved": retrieved,

        "latency_ms": round(
            latency_ms,
            2
        )
    }

    return trace


def save_results(results):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output = {
        "run_name": "policyiq_v3_baseline",

        "description": (
            "Frozen V3 baseline run using the "
            "selected PolicyIQ V2 retrieval pipeline."
        ),

        "total_questions_completed": len(results),

        "results": results
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2
        )


def warm_up():

    print("\n==============================")
    print("WARMING UP POLICYIQ")
    print("==============================")

    try:
        ask_policyiq(
            "What is No Claim Bonus?"
        )

        print("Warm-up complete.")

    except Exception as error:
        print(
            f"Warm-up failed: {error}"
        )

        print(
            "Continuing with evaluation..."
        )


def main():

    questions = load_questions()

    results = load_existing_results()

    completed_ids = {
        result["question_id"]
        for result in results
    }

    print("\n==============================")
    print("POLICYIQ V3 RAG EVALUATION")
    print("==============================")

    print(
        f"Total questions: {len(questions)}"
    )

    print(
        f"Already completed: {len(completed_ids)}"
    )

    print(
        f"Remaining: "
        f"{len(questions) - len(completed_ids)}"
    )

    # Only warm up if there are still
    # questions left to evaluate.
    if len(completed_ids) < len(questions):
        warm_up()

    for index, question in enumerate(
        questions,
        start=1
    ):

        question_id = question[
            "question_id"
        ]

        if question_id in completed_ids:

            print(
                f"\nSkipping {question_id} "
                "- already completed"
            )

            continue

        print(
            "\n=============================="
        )

        print(
            f"Running {question_id} "
            f"({index}/{len(questions)})"
        )

        print(
            "=============================="
        )

        try:

            trace = evaluate_question(
                question
            )

            results.append(
                trace
            )

            completed_ids.add(
                question_id
            )

            # Save immediately after
            # every successful question.
            save_results(
                results
            )

            print(
                f"Completed {question_id}"
            )

            print(
                f"Latency: "
                f"{trace['latency_ms']:.2f} ms"
            )

            print(
                f"Retrieved chunks: "
                f"{len(trace['retrieved'])}"
            )

        except KeyboardInterrupt:

            print(
                "\nEvaluation stopped manually."
            )

            print(
                "Completed results are already saved."
            )

            break

        except Exception as error:

            print(
                f"\nERROR on {question_id}: "
                f"{error}"
            )

            print(
                "Previous successful results "
                "are already saved."
            )

            print(
                "Stopping evaluation so the "
                "failure can be inspected."
            )

            break

    print(
        "\n=============================="
    )

    print(
        "V3 BASELINE STATUS"
    )

    print(
        "=============================="
    )

    print(
        f"Completed: "
        f"{len(results)}/{len(questions)}"
    )

    print(
        f"Saved to: {OUTPUT_PATH}"
    )

    if len(results) == len(questions):

        print(
            "\nV3 baseline run complete."
        )

        print(
            "Freeze this JSON before "
            "starting manual scoring."
        )

    else:

        print(
            "\nEvaluation is incomplete."
        )

        print(
            "Run the same command again "
            "to resume."
        )


if __name__ == "__main__":
    main()