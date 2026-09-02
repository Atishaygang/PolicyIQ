# ADR 007 — PolicyIQ V1 Architecture

> **Status:** Accepted  
> **Decision:** Modular, evidence-first RAG pipeline  
> **Project:** PolicyIQ V1

---

## Purpose

PolicyIQ is an insurance document-intelligence system designed to answer questions from real policy and regulatory documents while preserving evidence provenance.

The architecture deliberately separates each RAG stage so failures can be localized and evaluated.

## End-to-End Architecture

```text
                    POLICYIQ V1

                 11 Insurance PDFs
                         │
                         ▼
                Page-Level Loading
                    PyMuPDFLoader
                         │
                         ▼
              Conservative Cleaning
                         │
                         ▼
              430 Usable Page Docs
                         │
                         ▼
               Metadata Enrichment
                         │
                         ▼
            Recursive Chunking 1200/200
                         │
                         ▼
                    1,144 Chunks
                         │
                         ▼
        Multilingual MiniLM Embeddings
                 384-D normalized
                         │
                         ▼
                Persistent Chroma
                         │
                         ▼
                 Dense Retrieval
                 Top-5 for V1 RAG
                         │
                         ▼
           Explicit [SOURCE N] Context
                         │
                         ▼
                 Grounded Prompt
                         │
                         ▼
       GPT-OSS-120B via Hugging Face
                         │
                         ▼
              Answer + Source Citations
```

## Repository Structure

```text
Policy_IQ/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│   └── decisions/
│       ├── 001-vector-database.md
│       ├── 002-text-splitting.md
│       ├── 003-embedding-model.md
│       ├── 004-llm-provider.md
│       ├── 005-document-cleaning.md
│       ├── 006-corpus-ingestion-and-metadata.md
│       ├── 007-Architecture.md
│       └── 008-evaluation.md
│
├── evaluation/
│   ├── questions.json
│   └── evidence_coverage_results.json
│
├── src/
│   ├── ingestion/
│   ├── chunking/
│   ├── retrieval/
│   ├── evaluation/
│   └── rag/
│
├── tests/
├── .env.example
├── .gitignore
├── config.py
├── README.md
└── requirements.txt
```

## Stage Responsibilities

### Ingestion
Loads one LangChain `Document` per PDF page.

### Cleaning
Removes document-local boilerplate conservatively while preserving evidence.

### Metadata
Adds stable IDs, product/category information, and human-visible page numbers.

### Chunking
Uses the evidence-validated `1200 / 200` recursive splitting baseline.

### Embeddings
Uses normalized 384-dimensional multilingual MiniLM vectors.

### Vector Storage
Persists chunks in Chroma. Build and query paths are separate to prevent duplicate ingestion.

### Retrieval
Dense semantic similarity search returns candidate evidence. V1 generation uses Top-5.

### Context Construction
Every chunk becomes an explicit `[SOURCE N]` block containing document ID, filename, PDF page, and content.

### Generation
The LLM answers only from supplied context, cites source labels, avoids unsupported claim decisions, and abstains when evidence is insufficient.

## Failure-Localization Model

```text
Evidence missing from chunks
→ ingestion / cleaning / chunking problem

Evidence exists but is not retrieved
→ embedding / retrieval problem

Correct evidence retrieved but answer is wrong
→ prompt / LLM problem

No evidence exists but model answers anyway
→ grounding / abstention problem
```

## Output Design

The RAG pipeline currently keeps the generated answer and retrieved `Document` objects separate so a future API can return structured output:

```json
{
  "question": "...",
  "answer": "...",
  "sources": [
    {
      "document_id": "DOC001",
      "filename": "1_motor_policy.pdf",
      "page": 2
    }
  ]
}
```

## V1 Capabilities

- Real insurance corpus.
- Page-level provenance.
- Conservative cleaning.
- Evidence-validated chunking.
- Dense semantic retrieval.
- Persistent indexing.
- Grounded LLM generation.
- Source citations.
- Multi-source synthesis.
- Unanswerable-query abstention.

## V1 Limitations

- No BM25/hybrid retrieval.
- No reranker.
- No query rewriting.
- No metadata-aware routing.
- Fixed Top-5 generation context.
- No automatic citation verification.
- No structured Pydantic output yet.
- No production API/UI yet.

## Architectural Principle

> Every stage should be independently inspectable and evaluable.

## Final Decision

**PolicyIQ V1 adopts a modular, evidence-first RAG architecture with explicit separation between ingestion, retrieval, and grounded generation.**
