# PolicyIQ — Insurance Document Intelligence with RAG

> An evidence-first Retrieval-Augmented Generation system for insurance policies and regulatory documents.

---

## Overview

PolicyIQ is a modular RAG system built over real insurance-policy and IRDAI documents. Its goal is not merely to generate plausible answers, but to preserve evidence provenance, retrieve relevant policy wording, generate grounded responses, provide source citations, and abstain when the corpus does not support the question.

Instead of treating RAG as a single framework call, PolicyIQ validates each stage:

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
Vector Retrieval
  ↓
Grounded Prompt
  ↓
LLM
  ↓
Answer + Citations
```

## V1 Snapshot

```text
Insurance / regulatory PDFs: 11
Raw PDF pages: 431
Usable cleaned pages: 430
Chunk size / overlap: 1200 / 200
Final chunks: 1,144
Embedding dimension: 384
Golden questions: 24
Answerable golden questions: 19
Golden evidence coverage: 100%
Vector store: Chroma
Generation: GPT-OSS-120B via Hugging Face
```

## Why PolicyIQ

Insurance documents are difficult RAG inputs because they contain legal wording, definitions, exclusions, conditions, tables, repeated headers/footers, similar clauses across products, and regulatory guidance that must not be confused with insurer-specific wording.

PolicyIQ therefore treats provenance, validation, and failure analysis as first-class requirements.

## Architecture

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
Recursive Chunking 1200/200
  ↓
1,144 Chunks
  ↓
Multilingual MiniLM Embeddings (384-D)
  ↓
Persistent Chroma
  ↓
Dense Top-K Retrieval
  ↓
Explicit [SOURCE N] Context
  ↓
Grounded Prompt
  ↓
GPT-OSS-120B
  ↓
Answer + Source Citations
```

See `docs/decisions/007-Architecture.md` for the detailed design.

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
│   └── evidence_coverage_results.json
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

## Corpus and Provenance

The V1 corpus contains **11 real insurance/regulatory PDFs**, including motor-policy wording, health-policy wording, IRDAI regulations, master circulars, motor-insurance FAQ content, and service-provider guidance.

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

## Cleaning

Cleaning is conservative and document-local. PolicyIQ removes repeated headers/footers, boundary page labels, matching standalone page numbers, and empty lines while avoiding aggressive numeric deletion.

A two-stage cleaning fix was introduced after discovering that page numbers could survive if boundary positions were calculated before header removal.

See `005-document-cleaning.md`.

## Chunking

Final V1 baseline:

```text
RecursiveCharacterTextSplitter
chunk_size = 1200
chunk_overlap = 200
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

Most importantly, the strategy was validated against golden evidence before embeddings were introduced.

## Golden Evidence Coverage

```text
Answerable questions: 19
PASS: 19
PARTIAL: 0
FAIL: 0
Full evidence coverage: 100%
```

This established that the current ingestion + cleaning + chunking pipeline preserved all annotated answer evidence.

## Embeddings

Model:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Configuration:

```text
CPU
384 dimensions
normalized embeddings
```

Semantic smoke test:

```text
Related similarity: 0.7764
Unrelated similarity: 0.4419
Query dimension: 384
```

## Vector Store

PolicyIQ uses persistent Chroma.

A duplicate-ingestion bug was discovered when repeated builds against the same collection produced **4,576** vectors instead of **1,144**. Index creation and querying were separated into dedicated modules, and the clean collection now contains exactly **1,144 vectors**.

## Retrieval Evaluation

Strict exact-source/page Hit@K is recorded as a diagnostic baseline:

| Metric | Hits | Rate |
|---|---:|---:|
| Hit@1 | 6 / 19 | 31.6% |
| Hit@3 | 8 / 19 | 42.1% |
| Hit@5 | 12 / 19 | 63.2% |
| Hit@10 | 12 / 19 | 63.2% |
| Hit@15 | 14 / 19 | 73.7% |
| Hit@20 | 14 / 19 | 73.7% |

These numbers are **not presented as final RAG accuracy**. The current golden set does not enumerate every semantically valid alternative chunk, and some questions require evidence from multiple chunks/documents.

See `docs/decisions/008-evaluation.md`.

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

- Use only supplied context.
- Avoid outside knowledge.
- Avoid invented policy terms or claim decisions.
- Cite `[SOURCE N]`.
- Distinguish regulation from insurer policy wording.
- Avoid merging different policies into a universal rule.
- Abstain when evidence is insufficient.

## End-to-End V1 Tests

### Exact

```text
What depreciation applies to plastic parts?
```

Result: correct **50%** answer with multiple policy citations.

### Semantic

```text
Will damage be covered if the driver was drunk?
```

Result: PolicyIQ did not overgeneralize injury-related intoxication clauses into a vehicle-damage conclusion and correctly stated that the available excerpts were insufficient.

### Regulatory

```text
What obligations does an insurer have regarding policyholder grievances?
```

Result: grounded regulatory synthesis with citations.

### Unanswerable

```text
What will HDFC ERGO's share price be next month?
```

Result:

```text
I could not find sufficient information in the provided documents.
```

## V1 Capabilities

```text
✅ Real insurance corpus
✅ Page-level provenance
✅ Conservative cleaning
✅ Manifest-based metadata
✅ Chunking experiments
✅ 100% golden evidence coverage
✅ Multilingual dense embeddings
✅ Persistent vector store
✅ Semantic retrieval
✅ Retrieval diagnostics
✅ Grounded LLM generation
✅ Source citations
✅ Multi-source synthesis
✅ Unanswerable-query abstention
```

## V1 Limitations

V1 intentionally does not yet include:

- Hybrid BM25 + dense retrieval.
- Reranking.
- Query rewriting.
- Metadata-aware routing.
- Dynamic Top-K.
- Parent-child retrieval.
- Automatic citation verification.
- Structured Pydantic output.
- Production FastAPI layer.
- UI or authentication.

These are V2+ improvements rather than unfinished V1 fundamentals.

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

Create `.env` from `.env.example`. Never commit `.env`.

### Build vector store

Run the dedicated build module only when intentionally rebuilding the index.

### Run end-to-end RAG

```powershell
python -m src.rag.pipeline
```

## Engineering Lessons

1. Retrieval quality starts before embeddings.
2. Cleaning should be conservative and auditable.
3. Chunking should be validated against evidence, not intuition.
4. Persistent vector stores require deliberate build/query separation.
5. Exact source rank is useful but not identical to semantic answerability.
6. LLM grounding must prevent clause overgeneralization.
7. Unanswerable questions are essential hallucination tests.
8. RAG should be debugged layer by layer.

## V2 Direction

V2 should improve retrieval quality before adding random product features:

```text
Hybrid retrieval
   +
Metadata filters
   +
Query rewriting
   +
Reranking
   +
Better relevance judgments
   +
Structured responses
   +
Citation validation
```

## Status

**PolicyIQ V1: end-to-end RAG baseline operational.**
