# PolicyIQ V4 — Final Benchmark & V3 Comparison

## Status

V4 Reliability & Performance Hardening benchmark completed on the same frozen 24-question evaluation set used for V3.

- Total questions: 24
- Answerable: 19
- Unanswerable: 5
- V4 runtime configuration: Jina reranker on CPU with `torch.float32`
- Retrieval architecture unchanged: Dense + BM25 → RRF → Hybrid Top-10 → Jina reranker → Top-5 → grounded LLM
- Original conservative grounding/abstention prompt retained

---

## 1. Executive Summary

V4 achieved a major latency reduction without changing the retrieval architecture.

The median end-to-end latency fell from **99.97s in frozen V3 to 19.59s in V4**, a reduction of **80.4%** and roughly a **5.1× speedup**.

The primary reliability weakness remains unchanged: **4 of 19 answerable questions were falsely refused**. All **5 of 5 deliberately unanswerable questions were still correctly refused**.

V4 therefore materially improved performance while preserving conservative refusal behavior, but it did not solve the known retrieval/context failures.

---

## 2. V3 vs V4 Quality

| Metric | V3 Frozen | V4 Final | Change |
|---|---:|---:|---:|
| Faithfulness | 1.75/2 (n=16) | 1.93/2 (n=15) | +0.18 |
| Answer relevance | 1.368/2 (n=19) | 1.474/2 (n=19) | +0.106 |
| Citation correctness | 13 PASS, 3 PARTIAL (n=16) | 14 PASS, 1 PARTIAL (n=15) | improved |
| Citation completeness | 12 PASS, 4 PARTIAL (n=16) | 14 PASS, 1 PARTIAL (n=15) | improved |
| Correct unanswerable refusals | 5/5 | 5/5 | unchanged |
| False refusals on answerable questions | 4/19 | 4/19 | unchanged |

### Denominator caveat

Faithfulness and citation metrics do not use identical denominators across V3 and V4.

V3 had 16 citation/faithfulness-scored answerable responses, while V4 had 15 because Q008 produced a pure refusal under the retained conservative prompt. Therefore, the apparent improvement in these metrics should not be interpreted as a perfectly controlled quality gain.

Answer relevance remains directly comparable across all 19 answerable questions.

---

## 3. V3 vs V4 Latency

| Metric | V3 Frozen | V4 Final | Reduction |
|---|---:|---:|---:|
| Average | 104.93s | 21.75s | 79.3% |
| Median | 99.97s | 19.59s | 80.4% |
| P95 | 163.27s | 32.47s | 80.1% |
| Minimum | 68.40s | 15.20s | — |
| Maximum | 166.20s | 33.91s | — |

### Average V4 stage latency

- Hybrid retrieval: **0.05s**
- Jina reranking: **20.84s**
- LLM generation: **0.85s**
- Total end-to-end: **21.75s**

Jina reranking remains the dominant steady-state latency cost.

---

## 4. Known High-Severity Reliability Failures

### Q003 — Emergency hospitalization notification

The correct Optima Secure clause exists intact in the index at DOC004 page 49, but it is not surfaced by Dense Top-20, BM25 Top-20, Hybrid Top-20, query expansion, DOC004-only filtering, or a simplified query.

Classification:

**Retrieval / embedding-ranking limitation**

No benchmark-specific tuning was performed.

### Q004 — Optima Secure free-look period

The answerable question still results in a false refusal because the required evidence is not present in the final retrieved Top-5.

Classification:

**Retrieval/context failure**

### Q008 — Intoxicated driver and own-damage coverage

The conservative prompt still refuses.

A controlled prompt-relaxation experiment was tested with an identical frozen Top-5 context. The relaxed prompt produced mixed behavior and, in some runs, inferred vehicle own-damage coverage merely because no intoxication exclusion appeared in the retrieved excerpts.

That experiment was rejected because absence of an exclusion in the retrieved context is not sufficient evidence of coverage.

Updated classification:

**Retrieval/context insufficiency with generation instability under prompt relaxation**

The original conservative grounding prompt was retained.

### Q018 — Planned hospitalization + IRDAI duty

The multi-document question still falsely refuses because the required planned-hospitalization evidence is not surfaced in the final Top-5.

Classification:

**Retrieval/context failure**

---

## 5. Other Important Findings

### Q006 — Golden evidence limitation

Q006 retrieves valid evidence from DOC010 stating that the applicable premium refund after a free-look cancellation request must occur within 7 days.

The original golden annotations were created before DOC010/DOC011 were fully represented in expected evidence.

Therefore:

- strict expected `(document_id, page)` metrics remain useful for reproducibility;
- alternate valid evidence must sometimes be human-adjudicated.

### Q011 — Evidence-linking weakness

The answer correctly distinguishes cashless rejection from reimbursement, but the final explanation joins two separately retrieved procedures without a single explicit clause directly stating that reimbursement remains available after cashless denial.

V4 score:

- Faithfulness: 1/2
- Citation correctness: PARTIAL
- Citation completeness: PARTIAL

### Q019 — Partial retrieval improvement

The V4 answer gives strong HDFC deductible mechanics and a useful IRDAI loss-participation reference.

However, the fuller general deductible definition expected from the IRDAI FAQ is still absent.

V4 score:

- Faithfulness: 2/2
- Relevance: 1/2
- Citation correctness: PASS
- Citation completeness: PASS

---

## 6. V4 Engineering Decisions

V4 accepted the following:

1. Keep `jinaai/jina-reranker-v3`.
2. Run the reranker on CPU with `torch.float32`.
3. Keep Dense + BM25 + RRF hybrid retrieval.
4. Keep Hybrid Top-10 → reranked Top-5.
5. Retain stage-level latency instrumentation.
6. Retain the conservative grounding/abstention prompt.
7. Reject prompt relaxation that generates unsupported policy conclusions.
8. Document known retrieval failures rather than overfitting individual benchmark questions.
9. Do not change chunking or embeddings during V4 merely to improve individual benchmark cases.

---

## 7. Final V4 Assessment

V4 succeeded at its primary performance-hardening goal.

Median end-to-end latency improved from approximately **100 seconds to 19.6 seconds**, while all five deliberately unanswerable questions continued to be refused correctly.

The system's main remaining reliability limitation is not hallucination on the unanswerable set; it is **failure to retrieve sufficient evidence for some answerable questions**, producing a false-refusal rate of **4/19 (21.1%)**.

The next version should therefore focus on productionization rather than further benchmark-specific tuning, while carrying these retrieval limitations forward as explicitly documented technical debt.

---

## 8. V4 Exit Status

- FP32 CPU reranker hardening: COMPLETE
- Stage-level latency instrumentation: COMPLETE
- Known retrieval limitations documented: COMPLETE
- False-refusal/prompt consistency experiment: COMPLETE
- Final 24-question benchmark: COMPLETE
- Manual scoring: COMPLETE
- V3 vs V4 comparison: COMPLETE

**PolicyIQ V4 — Reliability & Performance Hardening: COMPLETE**
