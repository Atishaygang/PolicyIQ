import json
import time
from pathlib import Path

from src.rag.pipeline import ask_policyiq


QUESTIONS_PATH = Path(
    "evaluation/questions.json"
)

OUTPUT_PATH = Path(
    "evaluation/rag_runs/v4_final.json"
)

WARMUP_QUESTION = (
    "What is No Claim Bonus?"
)


def load_questions():

    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if isinstance(data, dict):
        return data["questions"]

    return data


def load_existing_results():

    if not OUTPUT_PATH.exists():
        return []

    with open(
        OUTPUT_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_results(results):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )


def serialize_document(doc):

    return {
        "document_id":
            doc.metadata.get(
                "document_id"
            ),

        "filename":
            doc.metadata.get(
                "filename"
            ),

        "pdf_page":
            doc.metadata.get(
                "pdf_page"
            ),

        "page_content":
            doc.page_content
    }


def main():

    questions = load_questions()

    existing_results = (
        load_existing_results()
    )

    completed_ids = {
        result["question_id"]
        for result in existing_results
    }


    print(
        "\n======================================"
    )
    print(
        "POLICYIQ V4 FINAL BENCHMARK"
    )
    print(
        "======================================"
    )

    print(
        f"Questions: {len(questions)}"
    )

    print(
        f"Already completed: "
        f"{len(completed_ids)}"
    )


    # ==========================================
    # Warm local components
    #
    # V3 also used a warm-up before the benchmark.
    # Keep this for fair V3 vs V4 comparison.
    # ==========================================

    print(
        "\nWarming pipeline..."
    )

    ask_policyiq(
        WARMUP_QUESTION
    )

    print(
        "Warm-up complete."
    )


    results = list(
        existing_results
    )


    for index, item in enumerate(
        questions,
        start=1
    ):

        question_id = item[
            "question_id"
        ]

        if question_id in completed_ids:

            print(
                f"\n[{index}/{len(questions)}] "
                f"{question_id} already completed."
            )

            continue


        question = item[
            "question"
        ]


        print(
            "\n======================================"
        )

        print(
            f"[{index}/{len(questions)}] "
            f"{question_id}"
        )

        print(
            "======================================"
        )

        print(
            question
        )


        try:

            # ==================================
            # Outer timing
            #
            # This is retained for direct
            # comparison with V3's benchmark
            # methodology.
            # ==================================

            start = time.perf_counter()

            result = ask_policyiq(
                question
            )

            end = time.perf_counter()


            end_to_end_ms = (
                end - start
            ) * 1000


            retrieved_documents = [
                serialize_document(doc)
                for doc
                in result[
                    "retrieved_documents"
                ]
            ]


            benchmark_result = {
                "question_id":
                    question_id,

                "category":
                    item.get(
                        "category"
                    ),

                "answerable":
                    item.get(
                        "answerable"
                    ),

                "question":
                    question,

                "answer":
                    result[
                        "answer"
                    ],

                "sources":
                    result[
                        "sources"
                    ],

                "retrieved_documents":
                    retrieved_documents,

                "timings":
                    result.get(
                        "timings",
                        {}
                    ),

                "end_to_end_ms":
                    end_to_end_ms
            }


            results.append(
                benchmark_result
            )


            # ==================================
            # Autosave after every question
            # ==================================

            save_results(
                results
            )


            print(
                "\nAnswer:"
            )

            print(
                result[
                    "answer"
                ]
            )


            print(
                "\nLatency:"
            )

            print(
                f"{end_to_end_ms / 1000:.2f}s"
            )


            if result.get(
                "timings"
            ):

                timings = result[
                    "timings"
                ]

                print(
                    f"Hybrid: "
                    f"{timings['hybrid_retrieval_ms'] / 1000:.2f}s"
                )

                print(
                    f"Reranking: "
                    f"{timings['reranking_ms'] / 1000:.2f}s"
                )

                print(
                    f"LLM: "
                    f"{timings['llm_generation_ms'] / 1000:.2f}s"
                )


            print(
                "\nRetrieved:"
            )

            for rank, source in enumerate(
                result["sources"],
                start=1
            ):

                print(
                    f"{rank}. "
                    f"{source['document_id']} "
                    f"| Page "
                    f"{source['page']}"
                )


        except Exception as error:

            print(
                f"\nFAILED {question_id}: "
                f"{error}"
            )

            print(
                "Progress saved. "
                "You can rerun the evaluator."
            )


    print(
        "\n======================================"
    )

    print(
        "V4 BENCHMARK COMPLETE"
    )

    print(
        "======================================"
    )

    print(
        f"Completed: "
        f"{len(results)}/{len(questions)}"
    )

    print(
        f"Saved to: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()