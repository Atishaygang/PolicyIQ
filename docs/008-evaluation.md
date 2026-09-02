# ADR 008 — Evaluation Strategy and V1 Baseline

> **Status:** Accepted  
> **Decision:** Layered evaluation with evidence-first validation  
> **Project:** PolicyIQ V1

---

## Purpose

PolicyIQ evaluates different RAG layers separately so a failure can be traced to the correct stage instead of being hidden behind a single final-answer score.

## Evaluation Model

```text
Question
  ↓
Did ingestion/chunking preserve the evidence?
  ↓
Can retrieval surface useful evidence?
  ↓
Can the LLM answer only from that evidence?
```

Failure localization:

```text
Evidence missing from chunks
→ ingestion/chunking issue

Evidence present but not retrieved
→ embedding/retrieval issue

Correct evidence retrieved but wrong answer
→ prompt/LLM issue

No evidence but model answers
→ grounding/abstention issue
```

## Golden Dataset

```text
Total questions: 24
Answerable: 19
Unanswerable: 5
```

Categories include exact, semantic, multi-document, and unanswerable questions.

## Golden Evidence Coverage

Before embeddings were introduced, PolicyIQ manually checked whether sufficient evidence survived cleaning and chunking.

```text
PASS: 19
PARTIAL: 0
FAIL: 0
Full evidence coverage: 100%
```

This validated the `1200 / 200` chunking baseline.

## Embedding Smoke Test

```text
Embedding dimension: 384
Related similarity: 0.7764347621601223
Unrelated similarity: 0.4418756010690164
Query embedding dimension: 384
```

## Vector-Store Validation

Expected count:

```text
1,144
```

A duplicate-ingestion bug temporarily produced **4,576** vectors. After separating build and query paths and rebuilding cleanly:

```text
Stored vectors: 1,144
```

## Strict Retrieval Diagnostic Baseline

PolicyIQ measured whether the exact expected `(document_id, pdf_page)` appeared in the ranking.

| Metric | Hits | Rate |
|---|---:|---:|
| Hit@1 | 6 / 19 | 31.6% |
| Hit@3 | 8 / 19 | 42.1% |
| Hit@5 | 12 / 19 | 63.2% |
| Hit@10 | 12 / 19 | 63.2% |
| Hit@15 | 14 / 19 | 73.7% |
| Hit@20 | 14 / 19 | 73.7% |

## Interpretation

This metric is retained as a **diagnostic**, not treated as final RAG accuracy.

Some questions require:

- Multiple chunks.
- Multiple documents.
- Evidence across pages.
- Semantically equivalent wording from another valid source.

Therefore:

```text
Exact source/page miss
≠ automatically poor semantic retrieval
```

The current golden data was designed mainly for evidence validation, not as exhaustive relevance judgments for every valid chunk. The baseline is recorded honestly rather than optimized against incomplete labels.

## End-to-End V1 Tests

### Exact

Question:

```text
What depreciation applies to plastic parts?
```

Observed: correct **50%** answer with multiple policy citations.

### Semantic

Question:

```text
Will damage be covered if the driver was drunk?
```

Observed: the model correctly avoided turning death/bodily-injury intoxication clauses into an unsupported vehicle-damage conclusion and stated that the available excerpts were insufficient.

### Regulatory

Question:

```text
What obligations does an insurer have regarding policyholder grievances?
```

Observed: grounded synthesis from regulatory sources with citations.

### Unanswerable

Question:

```text
What will HDFC ERGO's share price be next month?
```

Observed:

```text
I could not find sufficient information in the provided documents.
```

This validates basic abstention behavior.

## What V1 Does Not Claim

PolicyIQ V1 does **not** claim:

- 95% retrieval accuracy.
- Perfect ranking.
- Perfect citation correctness.
- Production-grade benchmark coverage.
- Automated claim decision accuracy.

## V2 Evaluation Priorities

- Multiple acceptable evidence labels per question.
- Chunk-level relevance judgments.
- Recall@K for multi-evidence questions.
- MRR / nDCG where appropriate.
- Semantic evidence sufficiency.
- Citation correctness.
- Faithfulness / groundedness.
- Abstention precision/recall.
- Hybrid retrieval and reranker comparisons.

## Final Decision

**PolicyIQ V1 freezes a layered evaluation baseline and avoids tuning the system to artificially maximize one incomplete metric.**
