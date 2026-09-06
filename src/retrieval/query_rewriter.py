from src.rag.llm import get_llm


QUERY_REWRITE_PROMPT = """
You rewrite user questions for document retrieval in an
insurance knowledge system.

Generate exactly 2 alternative search queries that preserve
the exact intent of the user's question.

Rules:
- Do not answer the question.
- Do not add facts that were not present.
- Preserve important numbers, policy terms and conditions.
- Use terminology that may appear in insurance policies,
  regulations, claim guidelines or FAQs.
- Each rewrite must express the same information need.
- Do not introduce a policy name, insurer, number, threshold,
  coverage, exclusion, condition, or fact unless it already
  appears in the question.
- Return only the two rewritten queries.
- Return one query per line.
- Do not number the queries.

Question:
{question}
"""


def rewrite_query(question):
    llm = get_llm()

    prompt = QUERY_REWRITE_PROMPT.format(
        question=question
    )

    response = llm.invoke(
        [
            ("human", prompt)
        ]
    )

    lines = [
        line.strip()
        for line in response.content.splitlines()
        if line.strip()
    ]

    return lines[:2]


def generate_queries(question):
    rewrites = rewrite_query(question)

    queries = [question]

    for rewrite in rewrites:
        if rewrite not in queries:
            queries.append(rewrite)

    return queries


if __name__ == "__main__":
    question = (
        "Will my insurance pay if the driver was drunk?"
    )

    queries = generate_queries(question)

    for index, query in enumerate(
        queries,
        start=1
    ):
        print(
            f"{index}. {query}"
        )