# ADR 009 — Keep Query Expansion as Optional Fallback

## Status
Accepted as optional; rejected as default

## Design
The original query is always retained. Two rewrites are generated, each passes through hybrid retrieval, results are fused, and the candidate pool is reranked once against the original query.

## Evaluation

| Pipeline | Hit@1 | Hit@3 | Hit@5 |
|---|---:|---:|---:|
| Hybrid + Reranker | 57.9% | 68.4% | 68.4% |
| + Query Expansion | 52.6% | 73.7% | 73.7% |

## Decision
Do not use query expansion on every request. It improves Top-3/Top-5 coverage but reduces Hit@1 and adds another model call.

## Final Decision
Retain as an optional fallback for difficult queries or future adaptive retrieval.
