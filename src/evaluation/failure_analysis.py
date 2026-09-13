import json
from pathlib import Path


MANUAL_SCORES_PATH = Path(
    "evaluation/reports/v3_manual_scores.json"
)

OUTPUT_PATH = Path(
    "evaluation/reports/v3_failure_analysis.json"
)


def load_scores():

    with open(
        MANUAL_SCORES_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data["scores"]


def classify_failure(score):

    qid = score["question_id"]

    if score["refusal_correct"] is False:

        if qid in {
            "Q003",
            "Q004",
            "Q018"
        }:
            return {
                "failure_type": "retrieval_failure",
                "secondary_type": "false_refusal",
                "severity": "high"
            }

        if qid == "Q008":
            return {
                "failure_type": "generation_interpretation_failure",
                "secondary_type": "false_refusal",
                "severity": "high"
            }

    if (
        score["citation_correctness"] == "PARTIAL"
        or
        score["citation_completeness"] == "PARTIAL"
    ):

        return {
            "failure_type": "citation_or_evidence_usage_issue",
            "secondary_type": "partial_support",
            "severity": "medium"
        }

    if score["answer_relevance"] == 1:

        return {
            "failure_type": "answer_completeness_issue",
            "secondary_type": "incomplete_or_indirect",
            "severity": "medium"
        }

    return {
        "failure_type": "no_material_failure",
        "secondary_type": None,
        "severity": "none"
    }


def build_analysis(scores):

    analyzed = []

    counts = {
        "retrieval_failure": 0,
        "generation_interpretation_failure": 0,
        "citation_or_evidence_usage_issue": 0,
        "answer_completeness_issue": 0,
        "no_material_failure": 0
    }

    high_severity = []
    medium_severity = []

    for score in scores:

        classification = classify_failure(
            score
        )

        counts[
            classification["failure_type"]
        ] += 1

        record = {
            "question_id": score[
                "question_id"
            ],

            "failure_type": classification[
                "failure_type"
            ],

            "secondary_type": classification[
                "secondary_type"
            ],

            "severity": classification[
                "severity"
            ],

            "notes": score[
                "notes"
            ]
        }

        analyzed.append(
            record
        )

        if (
            classification["severity"]
            == "high"
        ):
            high_severity.append(
                score["question_id"]
            )

        elif (
            classification["severity"]
            == "medium"
        ):
            medium_severity.append(
                score["question_id"]
            )

    return {
        "summary": {
            "total_questions": len(
                scores
            ),

            "failure_counts": counts,

            "high_severity_questions":
                high_severity,

            "medium_severity_questions":
                medium_severity
        },

        "failures": analyzed
    }


def save_analysis(analysis):

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
            analysis,
            file,
            indent=2
        )


def main():

    scores = load_scores()

    analysis = build_analysis(
        scores
    )

    save_analysis(
        analysis
    )

    print(
        "\n=============================="
    )

    print(
        "POLICYIQ V3 FAILURE ANALYSIS"
    )

    print(
        "=============================="
    )

    counts = analysis[
        "summary"
    ][
        "failure_counts"
    ]

    for failure_type, count in (
        counts.items()
    ):

        print(
            f"{failure_type}: {count}"
        )

    print(
        "\nHigh severity:"
    )

    print(
        analysis[
            "summary"
        ][
            "high_severity_questions"
        ]
    )

    print(
        "\nMedium severity:"
    )

    print(
        analysis[
            "summary"
        ][
            "medium_severity_questions"
        ]
    )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()