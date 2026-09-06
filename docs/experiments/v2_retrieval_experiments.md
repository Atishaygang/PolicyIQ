# PolicyIQ V2 Retrieval Experiments

## Rule
> Change one major retrieval variable at a time and record the result.

## V1 Dense Baseline

| Metric | Dense V1 |
|---|---:|
| Hit@1 | 31.6% |
| Hit@3 | 42.1% |
| Hit@5 | 63.2% |
| Hit@10 | 63.2% |
| Hit@15 | 73.7% |
| Hit@20 | 73.7% |

## Experiment 1 — Metadata Filtering
**Result:** no improvement in the controlled test.  
**Decision:** reject as hard default filtering because metadata categories overlap and cross-domain evidence is valid.

## Experiment 2 — BM25

| Metric | BM25 |
|---|---:|
| Hit@1 | 26.3% |
| Hit@3 | 42.1% |
| Hit@5 | 47.4% |
| Hit@10 | 57.9% |
| Hit@15 | 68.4% |
| Hit@20 | 73.7% |

**Decision:** keep as complementary lexical retrieval, not as standalone replacement.

## Experiment 3 — Hybrid RRF

| Metric | Dense V1 | Hybrid |
|---|---:|---:|
| Hit@1 | 31.6% | 42.1% |
| Hit@3 | 42.1% | 52.6% |
| Hit@5 | 63.2% | 68.4% |
| Hit@10 | 63.2% | 73.7% |
| Hit@15 | 73.7% | 84.2% |
| Hit@20 | 73.7% | 84.2% |

**Decision:** accepted.

## Experiment 4 — Hybrid + Jina Reranker

| Pipeline | Hit@1 | Hit@3 | Hit@5 |
|---|---:|---:|---:|
| Dense V1 | 31.6% | 42.1% | 63.2% |
| Hybrid + Reranker | 57.9% | 68.4% | 68.4% |

**Decision:** accepted as V2 default.

## Experiment 5 — Query Expansion

| Pipeline | Hit@1 | Hit@3 | Hit@5 |
|---|---:|---:|---:|
| Hybrid + Reranker | 57.9% | 68.4% | 68.4% |
| + Query Expansion | 52.6% | 73.7% | 73.7% |

**Decision:** not default. Keep as optional fallback for difficult queries.

## Final Selection
Dense + BM25 → RRF → Jina Reranker → Top 5.
