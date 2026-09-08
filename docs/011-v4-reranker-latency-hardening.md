# ADR 011 — V4 Reranker Latency Hardening

## Status

Accepted for V4 runtime evaluation.

Final acceptance remains subject to the complete V4 end-to-end benchmark.

---

## Context

PolicyIQ V3 completed end-to-end RAG evaluation using the frozen retrieval architecture:

User Query  
→ Dense Retrieval + BM25  
→ Reciprocal Rank Fusion  
→ Hybrid Top-10  
→ Jina Reranker  
→ Final Top-5  
→ Grounded LLM  
→ Answer + Citations

The V3 benchmark showed high end-to-end latency.

Before changing the architecture, V4 introduced stage-level latency profiling to identify the actual bottleneck.

---

## Baseline Profiling Result

A profiled query produced approximately:

- Hybrid retrieval: 0.08 s
- Jina reranking: 89.16 s
- LLM generation: 1.01 s
- Total: 90.25 s

The reranker accounted for approximately 98.8% of the measured query latency.

This demonstrated that:

- Chroma retrieval was not the dominant bottleneck.
- BM25 and RRF were not the dominant bottlenecks.
- LLM generation was not the dominant bottleneck.
- Jina reranking on CPU was the primary latency bottleneck.

---

## Investigation

The V3 reranker configuration used:

```python
dtype="auto"


The V4 experiment changed only the model dtype to:

dtype=torch.float32

The following components were kept unchanged:

Jina reranker model
Dense retriever
BM25 retriever
RRF fusion
Hybrid candidate count
Final Top-5 evidence count
Embedding model
Chroma index
Grounded generation pipeline
Result

With FP32 on CPU, representative warmed query runs showed approximately:

Jina reranking: 13–18 s
LLM generation: approximately 1–2 s
End-to-end query latency: approximately 15–20 s

A 19-question retrieval evaluation produced:

Hit@1: 47.4%
Hit@3: 73.7%
Hit@5: 73.7%
Average retrieval + reranking latency: 18.34 s

These results are not the final V4 end-to-end benchmark.

They are controlled hardening measurements used to decide whether the FP32 configuration should proceed to final evaluation.

Evaluation Caveat

The golden retrieval metric uses strict expected:

(document_id, pdf_page)

pairs.

The live corpus contains additional valid regulatory documents that were not fully represented in the original golden annotations.

For example, Q006 was reported as a strict retrieval miss, but manual inspection found valid evidence in DOC010 explicitly stating that a free-look cancellation premium refund must occur within 7 days.

Therefore, strict Hit@K remains the reproducible benchmark metric, while alternate valid evidence may require manual adjudication.

Q003 Reliability Investigation

Q003 asks about the notification timeline for emergency hospitalization under HDFC ERGO Optima Secure.

The expected evidence exists intact in the index at:

DOC004 — PDF page 49

The indexed clause states that notice must be provided:

Within 24 hours from the date of emergency hospitalization
or before discharge, whichever is earlier.

The following diagnostic paths failed to surface the expected evidence:

Dense Top-20
BM25 Top-20
Hybrid Top-20
Query expansion
DOC004-only metadata filtering
Simplified retrieval query

The evidence itself was verified as correctly:

extracted
chunked
indexed
stored with correct document/page metadata

Therefore Q003 is classified as a:

retrieval / embedding-ranking limitation

and not as:

ingestion failure
chunking failure
missing index data
RRF failure
reranker failure
generation failure

No further Q003-specific tuning was performed to avoid overfitting the benchmark to one question.

Decision

For V4:

Use torch.float32 for the Jina reranker on CPU.
Keep the existing Dense + BM25 + RRF + Jina architecture.
Keep Top-10 hybrid candidates and Final Top-5 evidence.
Preserve stage-level latency instrumentation.
Do not modify chunking or embeddings solely to force Q003 to pass.
Document known retrieval limitations rather than overfit individual benchmark questions.
Validate the complete change using the same frozen 24-question end-to-end evaluation set.
Trade-off

FP32 substantially improves CPU reranking latency, but the final decision must consider both:

performance
RAG quality

A faster configuration will not be considered successful if it causes a meaningful regression in:

faithfulness
answer relevance
citation quality
refusal behavior
retrieval coverage
V4 Exit Validation

The final V4 benchmark will compare V3 and V4 on:

faithfulness
answer relevance
citation correctness
citation completeness
correct refusals
false refusals
end-to-end latency
median latency
P95 latency

Only after this benchmark will the V4 performance-hardening result be considered final.


That gives us a permanent engineering record without keeping all the temporary Q003 scripts.

**V4.3 is done once this file is saved.**

Next is **V4.4 — false-refusal consistency testing**, where we specifically check whether the generation layer can behave inconsistently even when the correct evidence is already in its Top-5. We’ll keep that test small rather than rerunning all 24 questions yet.