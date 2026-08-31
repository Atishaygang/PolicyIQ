from src.chunking.splitter import split_documents
from src.ingestion.corpus import load_corpus

import json


# --------------------------------
# Output file
# --------------------------------

output_path = (
    r"D:\Policy_IQ\evaluation"
    r"\evidence_coverage_results.json"
)


# --------------------------------
# Allowed failure reasons
# --------------------------------

ALLOWED_FAILURE_REASONS = {
    "chunk_boundary",
    "page_boundary",
    "extraction_failure",
    "missing_context",
    "wrong_expected_page",
    "missing_source",
}


# --------------------------------
# Save results
# --------------------------------

def save_results(results, output_path):

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )


# --------------------------------
# Filter expected chunks
# --------------------------------

def get_expected_chunks(
    chunks,
    document_id,
    expected_pages
):

    return [
        chunk
        for chunk in chunks
        if (
            chunk.metadata["document_id"] == document_id
            and
            chunk.metadata["pdf_page"] in expected_pages
        )
    ]


# --------------------------------
# Normalize page format
# --------------------------------

def normalize_pages(expected_pages):

    if isinstance(expected_pages, int):
        return [expected_pages]

    return expected_pages


# --------------------------------
# Manual status input
# --------------------------------

def get_manual_status():

    while True:

        status = input(
            "\nStatus [PASS/PARTIAL/FAIL]: "
        ).strip().upper()

        if status in {
            "PASS",
            "PARTIAL",
            "FAIL"
        }:
            return status

        print(
            "Invalid status. "
            "Enter PASS, PARTIAL, or FAIL."
        )


# --------------------------------
# Failure reason input
# --------------------------------

def get_failure_reason(status):

    if status == "PASS":
        return None

    print("\nAllowed failure reasons:")

    for reason in sorted(
        ALLOWED_FAILURE_REASONS
    ):
        print("-", reason)

    while True:

        reason = input(
            "\nFailure reason: "
        ).strip()

        if reason in ALLOWED_FAILURE_REASONS:
            return reason

        print(
            "Invalid failure reason."
        )


# --------------------------------
# Calculate metrics
# --------------------------------

def calculate_metrics(results):

    total = len(results)

    if total == 0:

        print(
            "\nNo answerable questions evaluated."
        )

        return


    pass_count = sum(
        1
        for result in results
        if result["status"] == "PASS"
    )


    partial_count = sum(
        1
        for result in results
        if result["status"] == "PARTIAL"
    )


    fail_count = sum(
        1
        for result in results
        if result["status"] == "FAIL"
    )


    full_coverage_rate = (
        pass_count / total
    ) * 100


    partial_or_better_rate = (
        (pass_count + partial_count)
        / total
    ) * 100


    failure_rate = (
        fail_count / total
    ) * 100


    print(
        "\n=============================="
    )

    print(
        "EVIDENCE COVERAGE METRICS"
    )

    print(
        "=============================="
    )


    print(
        "Total answerable questions:",
        total
    )


    print(
        "PASS:",
        pass_count
    )


    print(
        "PARTIAL:",
        partial_count
    )


    print(
        "FAIL:",
        fail_count
    )


    print(
        "Full evidence coverage:",
        round(
            full_coverage_rate,
            2
        ),
        "%"
    )


    print(
        "PASS or PARTIAL coverage:",
        round(
            partial_or_better_rate,
            2
        ),
        "%"
    )


    print(
        "Failure rate:",
        round(
            failure_rate,
            2
        ),
        "%"
    )


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":


    # --------------------------------
    # 1. Load golden dataset
    # --------------------------------

    with open(
        r"D:\Policy_IQ\evaluation\questions.json",
        "r",
        encoding="utf-8"
    ) as file:

        golden_data = json.load(file)


    # --------------------------------
    # 2. Load cleaned corpus
    # --------------------------------

    corpus = load_corpus(
        data_dir=r"D:\Policy_IQ\data\raw",
        manifest_path=r"D:\Policy_IQ\data\menifest.csv"
    )


    # --------------------------------
    # 3. Generate chunks
    # Current baseline = 1200 / 200
    # --------------------------------

    chunks = split_documents(
        documents=corpus
    )


    # --------------------------------
    # 4. Store manual evaluations
    # --------------------------------

    results = []


    # --------------------------------
    # 5. Evaluate each question
    # --------------------------------

    for question in golden_data["questions"]:


        # Skip unanswerable questions
        if (
            question["category"]
            == "unanswerable"
        ):
            continue


        print(
            "\n\n========================================"
        )

        print(
            "Question ID:",
            question["question_id"]
        )

        print(
            "Category:",
            question["category"]
        )

        print(
            "Question:"
        )

        print(
            question["question"]
        )

        print(
            "========================================"
        )


        total_expected_chunks = 0


        # --------------------------------
        # A question may have
        # one or multiple evidence sources
        # --------------------------------

        for evidence in question[
            "expected_evidence"
        ]:


            document_id = evidence[
                "document_id"
            ]


            expected_pages = (
                evidence["page"]
            )


            expected_pages = (
                normalize_pages(
                    expected_pages
                )
            )


            expected_chunks = (
                get_expected_chunks(
                    chunks,
                    document_id,
                    expected_pages
                )
            )


            total_expected_chunks += len(
                expected_chunks
            )


            print(
                "\nExpected source:"
            )

            print(
                "Document:",
                document_id
            )

            print(
                "Pages:",
                expected_pages
            )


            # --------------------------------
            # No chunks found
            # --------------------------------

            if not expected_chunks:

                print(
                    "\nNO CHUNKS FOUND "
                    "FOR EXPECTED SOURCE"
                )

                continue


            # --------------------------------
            # Print matching chunks
            # --------------------------------

            for index, chunk in enumerate(
                expected_chunks,
                start=1
            ):


                print(
                    f"\n--- CHUNK {index} ---"
                )


                print(
                    "Document:",
                    chunk.metadata[
                        "document_id"
                    ]
                )


                print(
                    "Page:",
                    chunk.metadata[
                        "pdf_page"
                    ]
                )


                print(
                    "Characters:",
                    len(
                        chunk.page_content
                    )
                )


                print()


                print(
                    chunk.page_content
                )


        # --------------------------------
        # 6. Manual judgment
        # --------------------------------

        status = get_manual_status()


        # --------------------------------
        # 7. Supporting chunks
        # --------------------------------

        supporting_chunks_input = input(
            "Number of supporting chunks: "
        ).strip()


        try:

            supporting_chunks = int(
                supporting_chunks_input
            )

        except ValueError:

            supporting_chunks = 0


        # --------------------------------
        # 8. Failure reason
        # --------------------------------

        failure_reason = (
            get_failure_reason(
                status
            )
        )


        # --------------------------------
        # 9. Notes
        # --------------------------------

        notes = input(
            "Notes: "
        ).strip()


        # --------------------------------
        # 10. Store result
        # --------------------------------

        results.append(
            {
                "question_id":
                    question["question_id"],

                "status":
                    status,

                "supporting_chunks":
                    supporting_chunks,

                "failure_reason":
                    failure_reason,

                "notes":
                    notes
            }
        )


        # --------------------------------
        # 11. Save after each question
        # --------------------------------

        save_results(
            results,
            output_path
        )


        print(
            f"Saved progress after "
            f"{question['question_id']}"
        )


    # --------------------------------
    # 12. Final output
    # --------------------------------

    print(
        "\nResults saved to:"
    )

    print(
        output_path
    )


    # --------------------------------
    # 13. Calculate metrics
    # --------------------------------

    calculate_metrics(
        results
    )