# PolicyIQ — Insurance Document Intelligence with RAG

> An evidence-first Retrieval-Augmented Generation system for insurance policies and IRDAI regulatory documents.

---

## Overview

PolicyIQ is a modular insurance RAG system built over real policy and regulatory PDFs. The goal is not merely to generate plausible answers, but to preserve evidence provenance, retrieve the correct policy wording, generate grounded responses with source citations, and abstain when the supplied corpus does not support a conclusion.

The project is developed version-by-version so that each major decision is measurable:

```text
V1 — Core Grounded RAG
V2 — Retrieval Optimization
V3 — End-to-End Reliability Evaluation
V4 — Reliability & Performance Hardening
```

PolicyIQ treats RAG as a pipeline that must be tested layer by layer:

```text
Ingestion
  ↓
Cleaning
  ↓
Metadata
  ↓
Chunking
  ↓
Evidence Coverage
  ↓
Embeddings
  ↓
Dense + Lexical Retrieval
  ↓
Reciprocal Rank Fusion
  ↓
Reranking
  ↓
Grounded Prompt
  ↓
LLM
  ↓
Answer + Citations + Observability
```

---

## Current Snapshot — V4

```text
Insurance / regulatory PDFs: 11
Raw PDF pages: 431
Usable cleaned pages: 430
Chunk size / overlap: 1200 / 200
Final chunks: 1,144
Embedding dimension: 384
Golden questions: 24
Answerable questions: 19
Unanswerable questions: 5
Golden evidence coverage after ingestion/chunking: 100%

Vector store: Chroma
Dense embeddings: paraphrase-multilingual-MiniLM-L12-v2
Lexical retrieval: BM25
Fusion: Reciprocal Rank Fusion
Reranker: jinaai/jina-reranker-v3
Reranker runtime: CPU FP32
Generation: GPT-OSS-120B via Hugging Face
```

### V4 final benchmark

```text
Average end-to-end latency: 21.75 s
Median latency: 19.59 s
P95 latency: 32.47 s
Minimum latency: 15.20 s
Maximum latency: 33.91 s

Correct unanswerable refusals: 5 / 5
False refusals on answerable questions: 4 / 19
Answerable response rate: 15 / 19
```

V4 reduced median latency from **99.97 s in frozen V3 to 19.59 s**, approximately a **5.1× speedup**, while preserving correct refusal behavior on all five deliberately unanswerable questions.

---

## Why PolicyIQ

Insurance documents are difficult RAG inputs because they contain:

- legal and contractual wording;
- exclusions and exceptions;
- similar clauses across multiple products;
- tables and repeated headers/footers;
- policy-specific scope;
- insurer wording alongside regulatory wording;
- apparently contradictory clauses that may actually apply to different sections;
- questions that require evidence from more than one document.

A system can produce a fluent answer while still failing in retrieval, scope preservation, evidence use, citation completeness, or abstention.

PolicyIQ therefore treats **provenance, evaluation, failure analysis, and refusal behavior** as first-class requirements.

---

## Current Architecture

```text
11 PDFs
  ↓
Page-Level Loading
  ↓
Conservative Cleaning
  ↓
430 Usable Pages
  ↓
Manifest Metadata
  ↓
Recursive Chunking (1200 / 200)
  ↓
1,144 Chunks
  ↓
Multilingual MiniLM Embeddings (384-D)
  ↓
Persistent Chroma
  ↓
Dense Top-10 + BM25 Top-10
  ↓
Reciprocal Rank Fusion
  ↓
Hybrid Top-10
  ↓
Jina Reranker (CPU, FP32)
  ↓
Final Top-5 Evidence
  ↓
Explicit [SOURCE N] Context
  ↓
Conservative Grounded Prompt
  ↓
GPT-OSS-120B
  ↓
Answer + Source Citations + Stage Timings
```

The current runtime retrieval path is intentionally fixed for V4:

```text
Dense Retrieval + BM25
          ↓
          RRF
          ↓
     Hybrid Top-10
          ↓
      Jina Reranker
          ↓
       Final Top-5
          ↓
      Grounded LLM
```

Query expansion was tested in V2 but retained only as an experimental/fallback path rather than the default runtime path.

---

## Repository Structure

```text
Policy_IQ/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── decisions/
├── evaluation/
│   ├── questions.json
│   ├── rag_runs/
│   │   ├── v3_baseline.json
│   │   └── v4_final.json
│   └── reports/
│       ├── v3_manual_scores.json
│       ├── v3_latency_report.json
│       ├── v3_failure_analysis.json
│       ├── v3_benchmark_report.md
│       ├── v4_manual_scores.json
│       ├── v4_benchmark_report.md
│       └── v3_v4_comparison.json
├── src/
│   ├── ingestion/
│   ├── chunking/
│   ├── retrieval/
│   ├── evaluation/
│   └── rag/
├── tests/
├── .env.example
├── .gitignore
├── config.py
├── requirements.txt
└── README.md
```

---

## Corpus and Provenance

The corpus contains **11 real insurance/regulatory PDFs**, including:

- motor policy wording;
- health policy wording;
- IRDAI regulations;
- master circulars;
- motor insurance FAQ content;
- motor insurance service-provider guidance.

Stable internal IDs (`DOC001` … `DOC011`) are used so evaluation and provenance do not depend on filenames.

Each page/chunk preserves metadata such as:

```text
document_id
filename
document_type
issuer
insurer
product
category
pdf_page
year
file_path
```

---

## Ingestion and Cleaning

Documents are loaded page-by-page using PyMuPDF-based loading.

Cleaning is conservative and document-local. PolicyIQ removes repeated headers/footers, page labels, matching standalone page numbers, and empty lines while avoiding aggressive deletion that could damage policy wording.

A two-stage cleaning fix was introduced after discovering that page numbers could survive when boundary positions were calculated before header removal.

Final ingestion result:

```text
Raw page documents: 431
Usable cleaned page documents: 430
```

One source page was empty and therefore removed.

---

## Chunking

The frozen chunking configuration is:

```text
RecursiveCharacterTextSplitter
chunk_size = 1200
chunk_overlap = 200

Separators:
["\n\n", "\n", ". ", " ", ""]
```

Final statistics:

```text
Total chunks: 1,144
Average characters: 979.05
Median characters: 1,139
Minimum characters: 74
Maximum characters: 1,199
Chunks under 200 chars: 13
```

Chunking was validated before embedding/retrieval optimization.

### Golden evidence coverage

```text
Answerable questions: 19
PASS: 19
PARTIAL: 0
FAIL: 0
Full evidence coverage: 100%
```

This established that the ingestion + cleaning + chunking pipeline preserved all originally annotated answer evidence.

---

## Embeddings

Model:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Configuration:

```text
Device: CPU
Dimensions: 384
Normalized embeddings: yes
```

The embedding model is cached in-process and used by persistent Chroma retrieval.

---

## Vector Store

PolicyIQ uses persistent Chroma.

A duplicate-ingestion bug was discovered during V1 when repeated builds against the same collection produced **4,576 vectors instead of 1,144**.

Index construction and query access were then separated. The clean collection contains:

```text
1,144 vectors
```

---

# Version History

## V1 — Core Grounded RAG ✅

V1 established the complete baseline:

```text
PDF ingestion
→ cleaning
→ metadata
→ chunking
→ embeddings
→ Chroma
→ dense retrieval
→ grounded prompt
→ LLM
→ answer + citations
```

### V1 dense-retrieval diagnostic

Strict expected `(document_id, pdf_page)` Hit@K:

| Metric | Hits | Rate |
|---|---:|---:|
| Hit@1 | 6 / 19 | 31.6% |
| Hit@3 | 8 / 19 | 42.1% |
| Hit@5 | 12 / 19 | 63.2% |
| Hit@10 | 12 / 19 | 63.2% |
| Hit@15 | 14 / 19 | 73.7% |
| Hit@20 | 14 / 19 | 73.7% |

These are diagnostic retrieval metrics rather than end-to-end RAG accuracy.

The golden set does not enumerate every semantically valid alternative evidence location, and some questions require multiple pieces of evidence.

---

## V2 — Retrieval Optimization ✅

V2 improved retrieval before adding product features.

### V2.1 Metadata filtering

Hard metadata filtering was tested but not selected as the default because it could unnecessarily constrain retrieval.

Metadata remains important for provenance, debugging, and future routing.

### V2.2 BM25

Standalone BM25 provided a complementary lexical signal but was weaker than dense retrieval as a standalone retriever.

### V2.3 Hybrid retrieval with RRF

Dense and BM25 results were fused using Reciprocal Rank Fusion.

Benchmark candidate-pool result:

```text
Hit@1: 42.1%
Hit@3: 52.6%
Hit@5: 68.4%
Hit@10: 73.7%
Hit@15: 84.2%
Hit@20: 84.2%
```

The final runtime path uses:

```text
Dense Top-10
+
BM25 Top-10
↓
RRF
↓
Hybrid Top-10
```

### V2.4 Jina reranking

Model:

```text
jinaai/jina-reranker-v3
```

Historical reranker benchmark:

```text
Hit@1: 57.9%
Hit@3: 68.4%
Hit@5: 68.4%
```

The historical benchmark used a different experiment context/candidate pool from later V4 evaluation, so it is not treated as a controlled dtype comparison.

### V2.5 Query expansion

LLM-based query expansion improved deeper retrieval:

```text
Hit@1: 52.6%
Hit@3: 73.7%
Hit@5: 73.7%
```

However, it reduced Hit@1, added another model call, and introduced more retrieval noise.

Decision:

> Query expansion is retained as a fallback/experimental path, not the default retrieval strategy.

### V2 final runtime selection

```text
User Query
  ↓
Dense Top-10 + BM25 Top-10
  ↓
RRF
  ↓
Hybrid Top-10
  ↓
Jina Reranker
  ↓
Final Top-5
  ↓
Grounded LLM
```

---

## V3 — End-to-End Reliability Evaluation ✅ FROZEN

V3 froze the system architecture and evaluated whether PolicyIQ was actually reliable.

### Evaluation set

```text
Total questions: 24
Answerable: 19
Unanswerable: 5
```

The set includes:

- exact-clause retrieval;
- semantic/paraphrased retrieval;
- multi-document reasoning;
- deliberately unanswerable questions.

### Manual evaluation dimensions

Each applicable answer was scored for:

```text
Faithfulness
Answer relevance
Citation correctness
Citation completeness
Refusal correctness
Failure type
```

### V3 quality results

```text
Mean faithfulness: 1.75 / 2
Normalized faithfulness: 87.5%

Mean answer relevance: 1.368 / 2
Normalized relevance: 68.4%

Citation correctness:
13 PASS
3 PARTIAL
(n = 16 citation-scored answers)

Citation completeness:
12 PASS
4 PARTIAL
(n = 16 citation-scored answers)

Correct unanswerable refusals: 5 / 5
False refusals on answerable questions: 4 / 19
Answerable response rate: 15 / 19
```

Important: citation metrics are calculated only over responses for which citations were applicable, not over all 24 questions.

### V3 failure analysis

```text
Retrieval failure: 3
Generation / interpretation failure: 1
Citation or evidence-use issue: 3
Answer-completeness issue: 2
No material failure: 15
```

High-severity benchmark failures:

```text
Q003
Q004
Q008
Q018
```

### V3 latency

```text
Average: 104.93 s
Median: 99.97 s
P95: 163.27 s
Minimum: 68.40 s
Maximum: 166.20 s
```

This benchmark is frozen and should not be mixed with later V4 measurements.

---

## V4 — Reliability & Performance Hardening ✅ COMPLETE

V4 did not add product features.

Its goal was to use V3 evidence to harden latency and reliability without rewriting the architecture.

### Stage-level profiling

An initial profiled query showed:

```text
Hybrid retrieval: 0.08 s
Jina reranking: 89.16 s
LLM generation: 1.01 s
Total: 90.25 s
```

The Jina reranker accounted for almost all end-to-end latency.

### FP32 CPU hardening

The V3 reranker loaded using:

```python
dtype="auto"
```

V4 changed the Jina CPU runtime to:

```python
dtype=torch.float32
```

The model, retrieval architecture, candidate counts, Top-5 behavior, embedding model, vector store, and grounded generation path remained unchanged.

### V4 final latency benchmark

The same frozen 24-question benchmark was rerun after the FP32 hardening:

| Metric | V3 Frozen | V4 Final | Reduction |
|---|---:|---:|---:|
| Average | 104.93 s | 21.75 s | 79.3% |
| Median | 99.97 s | 19.59 s | 80.4% |
| P95 | 163.27 s | 32.47 s | 80.1% |
| Minimum | 68.40 s | 15.20 s | — |
| Maximum | 166.20 s | 33.91 s | — |

Median latency improved by approximately **5.1×**.

Average V4 stage latency:

```text
Hybrid retrieval: ~0.05 s
Jina reranking: ~20.84 s
LLM generation: ~0.85 s
Total end-to-end: 21.75 s
```

The reranker is still the dominant steady-state latency cost.

### V4 quality results

```text
Faithfulness: 1.93 / 2
Faithfulness denominator: 15 non-refusal answerable responses

Answer relevance: 1.474 / 2
Answer relevance denominator: 19 answerable questions

Citation correctness:
14 PASS
1 PARTIAL
(n = 15)

Citation completeness:
14 PASS
1 PARTIAL
(n = 15)

Correct unanswerable refusals: 5 / 5
False refusals on answerable questions: 4 / 19
Answerable response rate: 15 / 19
```

### Quality-comparison caveat

V3 and V4 faithfulness/citation denominators are not identical.

V3 had 16 citation/faithfulness-scored responses, while V4 had 15 because one answerable benchmark item produced a pure refusal under the retained conservative prompt.

Therefore, the apparent increase in faithfulness and citation PASS rates is useful but should **not** be interpreted as a perfectly controlled quality gain.

Answer relevance remains directly comparable across all 19 answerable questions.

---

## Known V4 Reliability Limitations

### Q003 — Emergency hospitalization notification

The correct Optima Secure clause exists intact in the index at `DOC004`, PDF page 49.

It was still not surfaced by:

```text
Dense Top-20
BM25 Top-20
Hybrid Top-20
Query expansion
DOC004-only metadata filtering
Simplified retrieval query
```

Classification:

> Retrieval / embedding-ranking limitation.

The project intentionally did not overfit the system to force this one benchmark question to pass.

### Q004 — Optima Secure free-look period

The answerable question still produces a false refusal because sufficient evidence does not reach the final Top-5.

Classification:

> Retrieval/context failure.

### Q008 — Intoxicated driver and own-damage coverage

A controlled prompt-relaxation experiment was performed with an identical frozen Top-5 context.

The relaxed prompt produced inconsistent answers and, in some runs, inferred own-damage coverage merely because an intoxication exclusion was not visible in the retrieved excerpts.

That is unsafe:

```text
absence of exclusion in retrieved context
≠
evidence of coverage
```

The relaxed prompt was therefore rejected.

Classification:

> Retrieval/context insufficiency, with generation instability under prompt relaxation.

The original conservative grounding/abstention prompt remains the accepted configuration.

### Q018 — Planned hospitalization + broader IRDAI duty

The question still falsely refuses because the required planned-hospitalization evidence is not surfaced in the final Top-5.

Classification:

> Retrieval/context failure.

---

## Golden-Evidence Limitation

The original golden annotations primarily represented `DOC001`–`DOC009`, while the live corpus also contains `DOC010` and `DOC011`.

This matters for strict expected `(document_id, pdf_page)` evaluation.

For example, Q006 was reported as a strict retrieval miss in one diagnostic run, but manual inspection found valid evidence in `DOC010` explicitly stating the applicable **7-day** free-look refund timeline.

Therefore:

> strict expected-pair Hit@K is retained for reproducibility, but alternate valid evidence may require human adjudication.

---

## Grounded Generation

Retrieved chunks are converted to explicit source blocks:

```text
[SOURCE 1]
Document ID: DOC002
Filename: 2_motor_policy.pdf
PDF Page: 4
Content:
...
```

The generation prompt requires the LLM to:

- use only supplied context;
- avoid outside knowledge;
- avoid invented policy terms or claim decisions;
- cite `[SOURCE N]`;
- preserve policy/section/coverage scope;
- distinguish regulation from insurer-specific policy wording;
- avoid merging different policies into a universal rule;
- include relevant conditions, exceptions, and qualifications;
- abstain when evidence is insufficient.

The accepted V4 prompt remains deliberately conservative.

---

## Observability

`ask_policyiq()` returns stage timings with the response:

```text
hybrid_retrieval_ms
reranking_ms
context_prompt_ms
llm_client_ms
llm_generation_ms
response_build_ms
total_ms
```

This allows latency to be attributed to specific RAG stages rather than treating the pipeline as a black box.

---

## Evaluation Philosophy

PolicyIQ uses four failure locations when debugging:

```text
Answer missing from chunks
→ ingestion / chunking problem

Answer exists in chunks but is not retrieved
→ embedding / retrieval problem

Correct evidence is retrieved but answer is wrong
→ generation / prompt / interpretation problem

No supporting evidence exists but model answers anyway
→ grounding / abstention problem
```

This prevents random tuning and makes failures explainable.

A wrong answer is not automatically an LLM failure.

---

## Running the Project

### Create environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Configure secrets

Create `.env` from `.env.example`.

Never commit `.env`.

### Build vector store

Run the dedicated vector-store build module only when intentionally rebuilding the index.

### Run end-to-end PolicyIQ

```powershell
python -m src.rag.pipeline
```

### Run V4 final benchmark

```powershell
python -m src.evaluation.v4_rag_eval
```

---

## Engineering Lessons

1. Retrieval quality starts before embeddings.
2. Cleaning should be conservative and auditable.
3. Chunking should be validated against evidence, not intuition.
4. Persistent vector stores require deliberate build/query separation.
5. Dense and lexical retrieval provide complementary signals.
6. Exact source/page Hit@K is useful but is not identical to semantic answerability.
7. Reranking quality and reranking runtime are separate engineering concerns.
8. RAG latency must be profiled by pipeline stage.
9. A faster configuration is not acceptable if it weakens grounding.
10. Prompt relaxation can reduce refusals while simultaneously increasing unsupported conclusions.
11. Unanswerable questions are essential hallucination tests.
12. RAG failures should be classified before they are optimized.
13. Benchmark annotations can themselves be incomplete.
14. Reliability requires measuring failure modes, not just showing successful demos.

---

## Current Status

```text
V1 — Core Grounded RAG                         ✅ FROZEN
V2 — Retrieval Optimization                    ✅ COMPLETE
V3 — End-to-End Reliability Evaluation         ✅ FROZEN
V4 — Reliability & Performance Hardening       ✅ COMPLETE
```

### Current headline

```text
24-question reliability benchmark
19 answerable / 5 unanswerable

V3 median latency: 99.97 s
V4 median latency: 19.59 s

V3 P95: 163.27 s
V4 P95: 32.47 s

Correct unanswerable refusals: 5 / 5
False refusals on answerable questions: 4 / 19
```

---

## Next Direction — V5

V5 moves from experimental RAG hardening toward productionization.

Planned direction:

```text
FastAPI service layer
Structured request / response contracts
Health and readiness endpoints
Configuration cleanup
Production-safe error handling
Persisted evaluation / observability hooks
Containerization
API-level testing
```

The known V4 retrieval limitations remain documented technical debt rather than being hidden or benchmark-overfit.

---

## Project Principle

> A RAG system is not reliable because it answers a few demo questions correctly. Reliability starts when its evidence, failures, citations, refusals, and performance are measurable.
