# ADR 008 — Use Jina Reranker After Hybrid Retrieval

## Status
Accepted

## Decision
Use `jinaai/jina-reranker-v3` after hybrid retrieval and keep the final Top 5 chunks.

## Evaluation

| Pipeline | Hit@1 | Hit@3 | Hit@5 |
|---|---:|---:|---:|
| Dense V1 | 31.6% | 42.1% | 63.2% |
| Hybrid + Reranker | 57.9% | 68.4% | 68.4% |

## Interpretation
The reranker substantially improves early-rank precision and better uses the final context budget.

## Operational Note
The model is computationally expensive on CPU, so it is cached in-process and loaded only once per runtime/evaluation process.

## Final Decision
Hybrid + reranker is the default V2 retrieval path.
