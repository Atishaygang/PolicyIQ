import json
import statistics
from pathlib import Path


BASELINE_PATH = Path(
    "evaluation/rag_runs/v3_baseline.json"
)

OUTPUT_PATH = Path(
    "evaluation/reports/v3_latency_report.json"
)


def load_latencies():

    with open(
        BASELINE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    latencies = [
        result["latency_ms"]
        for result in data["results"]
    ]

    return latencies


def percentile(values, percentile_value):

    values = sorted(values)

    index = (
        percentile_value
        / 100
    ) * (
        len(values) - 1
    )

    lower = int(index)
    upper = min(
        lower + 1,
        len(values) - 1
    )

    weight = index - lower

    return (
        values[lower] * (1 - weight)
        +
        values[upper] * weight
    )


def build_report(latencies):

    average = statistics.mean(
        latencies
    )

    median = statistics.median(
        latencies
    )

    p95 = percentile(
        latencies,
        95
    )

    minimum = min(
        latencies
    )

    maximum = max(
        latencies
    )

    report = {
        "total_queries": len(latencies),

        "average_latency_ms": round(
            average,
            2
        ),

        "median_latency_ms": round(
            median,
            2
        ),

        "p95_latency_ms": round(
            p95,
            2
        ),

        "minimum_latency_ms": round(
            minimum,
            2
        ),

        "maximum_latency_ms": round(
            maximum,
            2
        ),

        "average_latency_seconds": round(
            average / 1000,
            2
        ),

        "median_latency_seconds": round(
            median / 1000,
            2
        ),

        "p95_latency_seconds": round(
            p95 / 1000,
            2
        )
    }

    return report


def save_report(report):

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
            report,
            file,
            indent=2
        )


def main():

    latencies = load_latencies()

    report = build_report(
        latencies
    )

    save_report(
        report
    )

    print(
        "\n=============================="
    )

    print(
        "POLICYIQ V3 LATENCY REPORT"
    )

    print(
        "=============================="
    )

    print(
        f"Queries: "
        f"{report['total_queries']}"
    )

    print(
        f"Average: "
        f"{report['average_latency_seconds']} s"
    )

    print(
        f"Median: "
        f"{report['median_latency_seconds']} s"
    )

    print(
        f"P95: "
        f"{report['p95_latency_seconds']} s"
    )

    print(
        f"Minimum: "
        f"{report['minimum_latency_ms']} ms"
    )

    print(
        f"Maximum: "
        f"{report['maximum_latency_ms']} ms"
    )

    print(
        f"\nSaved to: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()