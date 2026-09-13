# PolicyIQ

PolicyIQ is a production-style insurance document intelligence system built with grounded Retrieval-Augmented Generation (RAG).

It answers questions from a curated corpus of authentic insurance policies, FAQs, IRDAI regulations, circulars, and guidelines.

> Retrieve evidence first, answer only from that evidence, and abstain when the evidence is insufficient.

## Current Status

**Current version: V5 — Production API & Serving Layer**

Completed:

- PDF ingestion and metadata enrichment
- document cleaning and chunking
- multilingual dense retrieval
- BM25 sparse retrieval
- Reciprocal Rank Fusion
- Jina reranking
- grounded LLM generation
- source citations
- explicit abstention behavior
- golden-set evaluation
- latency profiling and hardening
- FastAPI serving layer
- Pydantic schemas
- startup preloading
- `/health` and `/ready`
- production error handling
- API tests
- Dockerized backend
- portable runtime paths

V5 intentionally does not retune the frozen RAG core. It focuses on serving, reliability, portability, and deployment.

---

## Architecture

```text
User Question
     ↓
FastAPI /api/v1/query
     ↓
Dense Top 10 + BM25 Top 10
     ↓
Reciprocal Rank Fusion
     ↓
Hybrid Top 10
     ↓
Jina Reranker v3
     ↓
Top 5 evidence chunks
     ↓
Grounded prompt
     ↓
Hugging Face hosted LLM
     ↓
Answer + Sources + Timings
```

---

## Corpus

PolicyIQ uses 11 authentic public insurance documents, including HDFC ERGO policies, IRDAI regulations, circulars, FAQs, and motor-insurance guidelines.

| Metric | Value |
|---|---:|
| PDFs | 11 |
| Raw page documents | 431 |
| Usable page documents | 430 |
| Chunks | 1,144 |
| Chunk size | 1,200 chars |
| Chunk overlap | 200 chars |
| Average chunk length | ~979 chars |
| Median chunk length | ~1,139 chars |

---

## Retrieval Stack

### Dense Retrieval

Embedding model:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

- CPU inference
- normalized embeddings
- 384-dimensional vectors
- Chroma vector store

### Sparse Retrieval

BM25 runs over the same cleaned and chunked corpus.

```text
rank-bm25
```

### Fusion

Dense and BM25 candidates are merged using Reciprocal Rank Fusion.

### Reranking

```text
jinaai/jina-reranker-v3
```

The reranker receives the hybrid candidate set and selects the final Top 5 chunks used by generation.

---

## Grounding and Abstention

The LLM is instructed to answer only from retrieved evidence.

If sufficient evidence is not present, PolicyIQ returns:

```text
I could not find sufficient information in the provided documents.
```

This is a valid `200 OK` product response, not an API error.

---

# Version History

## V1 — Core Grounded RAG

V1 established ingestion, cleaning, recursive chunking, embeddings, Chroma, dense retrieval, grounded generation, citations, and abstention.

Strict expected-pair retrieval results:

| K | Hit@K |
|---:|---:|
| 1 | 31.6% |
| 3 | 42.1% |
| 5 | 63.2% |
| 10 | 63.2% |
| 15 | 73.7% |
| 20 | 73.7% |

---

## V2 — Retrieval Optimization

V2 added:

- BM25
- hybrid retrieval
- Reciprocal Rank Fusion
- Jina reranking
- query-expansion experiments

Hybrid retrieval improved deeper recall, while reranking improved top-ranked evidence quality.

Query expansion was not made the default because it increased latency and sometimes introduced retrieval noise.

---

## V3 — End-to-End Reliability Evaluation

Golden set: 24 questions

- 7 exact
- 7 semantic
- 5 multi-document
- 5 unanswerable

Frozen V3 quality:

| Metric | Result |
|---|---:|
| Faithfulness | 1.75 / 2 |
| Relevance | 1.368 / 2 |
| Correct unanswerable refusals | 5 / 5 |
| False refusals | 4 / 19 |
| Answerable response rate | 15 / 19 |

Frozen V3 latency:

| Metric | Time |
|---|---:|
| Average | 104.93 s |
| Median | 99.97 s |
| P95 | 163.27 s |
| Min | 68.40 s |
| Max | 166.20 s |

The reranker was the dominant bottleneck.

---

## V4 — Reliability & Performance Hardening

V4 focused on performance and failure analysis without changing the overall RAG architecture.

Frozen V4 latency:

| Metric | V3 | V4 |
|---|---:|---:|
| Average | 104.93 s | **21.75 s** |
| Median | 99.97 s | **19.59 s** |
| P95 | 163.27 s | **32.47 s** |
| Min | 68.40 s | **15.20 s** |
| Max | 166.20 s | **33.91 s** |

Approximate median speedup:

```text
~5.1x
```

Frozen V4 quality:

| Metric | Result |
|---|---:|
| Faithfulness | 1.93 / 2 |
| Relevance | 1.474 / 2 |
| Citation correctness | 14 PASS, 1 PARTIAL |
| Citation completeness | 14 PASS, 1 PARTIAL |
| Correct unanswerable refusals | 5 / 5 |
| False refusals | 4 / 19 |
| Answerable response rate | 15 / 19 |

Important evaluation note: V3 and V4 faithfulness/citation denominators are not identical, so those quality changes should not be treated as perfectly controlled. Relevance uses the same 19-answerable-question denominator.

A relaxed grounding prompt was explicitly rejected after it produced unsupported coverage answers in some runs.

---

## V5 — Production API & Serving Layer

V5 productionizes the frozen evaluated RAG layer.

Added:

- FastAPI
- Pydantic request/response models
- `/api/v1/query`
- startup preloading
- `/health`
- `/ready`
- production-style error handling
- API tests
- Docker
- portable runtime paths

A single Docker run is not a replacement for the frozen V4 benchmark.

Example V5 Docker observation:

```text
Hybrid retrieval    ~0.09 s
Jina reranking      ~36.85 s
LLM generation      ~1.09 s
Total               ~38.02 s
```

This is one containerized runtime observation only.

---

# API

## Health

```http
GET /health
```

```json
{
  "service": "PolicyIQ API",
  "status": "running",
  "version": "5.0"
}
```

## Readiness

```http
GET /ready
```

```json
{
  "service": "PolicyIQ API",
  "ready": true
}
```

## Query

```http
POST /api/v1/query
```

Request:

```json
{
  "question": "What is maximum No Claim Bonus?"
}
```

Response shape:

```json
{
  "question": "What is maximum No Claim Bonus?",
  "answer": "...",
  "sources": [
    {
      "document_id": "DOC009",
      "filename": "Motor Insurance_FAQ.pdf",
      "page": 2
    }
  ],
  "timings": {
    "hybrid_retrieval_ms": 0.0,
    "reranking_ms": 0.0,
    "context_prompt_ms": 0.0,
    "llm_client_ms": 0.0,
    "llm_generation_ms": 0.0,
    "response_build_ms": 0.0,
    "total_ms": 0.0
  }
}
```

---

# Project Structure

```text
Policy_IQ/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── dependencies.py
│   ├── chunking/
│   ├── evaluation/
│   ├── ingestion/
│   ├── rag/
│   └── retrieval/
├── data/
│   ├── raw/
│   ├── processed/
│   └── menifest.csv
├── evaluation/
│   ├── questions.json
│   ├── rag_runs/
│   └── reports/
├── tests/
│   └── api/
├── docs/
├── config.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example
└── README.md
```

`menifest.csv` is intentionally kept with its existing filename during V5 to avoid unnecessary unrelated changes.

---

# Local Setup

## 1. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

## 3. Environment variables

Create `.env`:

```env
HUGGINGFACEHUB_ACCESS_TOKEN=hf_your_token_here
HF_TOKEN=hf_your_token_here
```

Never commit `.env`.

## 4. Run FastAPI

```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# Docker

## Build

```powershell
docker build -t policyiq-backend:v5 .
```

## Run

```powershell
docker run --name policyiq-v5 --env-file .env -p 8000:8000 policyiq-backend:v5
```

Useful endpoints:

```text
http://localhost:8000/health
http://localhost:8000/ready
http://localhost:8000/docs
```

Stop:

```powershell
docker stop policyiq-v5
```

Remove:

```powershell
docker rm policyiq-v5
```

Recreate:

```powershell
docker rm -f policyiq-v5
docker run --name policyiq-v5 --env-file .env -p 8000:8000 policyiq-backend:v5
```

---

# Portable Runtime Paths

Runtime paths are derived from the project root with `pathlib`.

Conceptually:

```python
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MANIFEST_PATH = DATA_DIR / "menifest.csv"
```

This allows the same serving code to resolve correctly on both Windows and Linux/Docker.

---

# Testing

Run:

```powershell
python -m pytest tests/api -v
```

API tests cover:

- health
- readiness
- request validation
- successful query contract
- abstention
- internal service errors

Heavy RAG evaluation is kept separate from lightweight API contract tests.

---

# Error Semantics

## Valid abstention

```text
HTTP 200
```

```text
I could not find sufficient information in the provided documents.
```

## Not ready

```text
HTTP 503
```

## Internal processing failure

```text
HTTP 500
```

The public response is generic while the server logs the full traceback.

---

# Startup Preloading

PolicyIQ preloads:

- embedding model
- vector store
- BM25 corpus
- Jina reranker
- LLM client

This removes initialization work from the first user request.

It does not remove the per-query CPU cost of reranking.

---

# Known Limitations

1. CPU reranking remains the largest latency bottleneck.
2. Four answerable golden questions still produce false refusals: `Q003`, `Q004`, `Q008`, `Q018`.
3. Fresh Docker containers may download Hugging Face model files during startup.
4. Multiple Uvicorn workers are not recommended yet because each worker would load its own model copies.
5. The live corpus contains documents added after the earliest expected-evidence design, so some valid evidence may exist outside the original golden expected pairs.

---

# Engineering Principles

```text
Measure before optimizing.
Freeze evaluated versions.
Separate retrieval failures from generation failures.
Do not loosen grounding just to increase answer rate.
Treat abstention as valid product behavior.
Do not modify the RAG core while productionizing the serving layer.
```

Failure diagnosis:

```text
Answer missing from chunks
→ ingestion/chunking

Answer exists but is not retrieved
→ embedding/retrieval/ranking

Correct evidence retrieved but answer is wrong
→ generation/prompt/LLM

No evidence but model answers
→ grounding/abstention
```

---

# Git Milestones

```text
v1.0   Core grounded RAG
v2.0   Retrieval optimization
v3.0   Reliability evaluation
v4.0   Reliability + performance hardening
v5.0   Production API + Docker serving
```

V4 should remain frozen as the evaluated reliability/performance milestone.

V5 development branch:

```text
v5-production-api
```

---

# Roadmap

Potential V6:

- LangGraph orchestration
- tool-based policy lookup
- controlled multi-step reasoning
- policy comparison workflows
- structured claim workflows

LangGraph should only be added if it creates real product value.

---

PolicyIQ is a portfolio and engineering project focused on grounded enterprise-style RAG, evaluation, reliability analysis, API serving, and containerization.
