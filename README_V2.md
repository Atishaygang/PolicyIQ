# PolicyIQ V2 — Retrieval Optimization

## Objective
Improve retrieval quality without breaking the frozen V1 RAG baseline.

## Frozen V1 Components
- Corpus
- Cleaning pipeline
- Chunking: 1200 / 200
- Embedding model
- Chroma vector store
- Grounded prompt
- LLM generation layer
- Golden evaluation set

## V2 Progression

### V2.1 Metadata Filtering
Status: **Tested, not selected**

Hard metadata filtering did not improve the controlled test and can remove valid cross-domain evidence. Metadata remains useful for provenance, analysis, routing hints, and future soft constraints.

### V2.2 BM25
Status: **Completed**

| Metric | BM25 |
|---|---:|
| Hit@1 | 26.3% |
| Hit@3 | 42.1% |
| Hit@5 | 47.4% |
| Hit@10 | 57.9% |
| Hit@15 | 68.4% |
| Hit@20 | 73.7% |

BM25 was weaker than dense retrieval standalone, but useful as a complementary lexical signal.

### V2.3 Hybrid Retrieval
Status: **Completed and selected**

Dense retrieval and BM25 are fused with Reciprocal Rank Fusion (RRF).

| Metric | Dense V1 | Hybrid |
|---|---:|---:|
| Hit@1 | 31.6% | 42.1% |
| Hit@3 | 42.1% | 52.6% |
| Hit@5 | 63.2% | 68.4% |
| Hit@10 | 63.2% | 73.7% |
| Hit@15 | 73.7% | 84.2% |
| Hit@20 | 73.7% | 84.2% |

### V2.4 Reranking
Status: **Completed and selected as default**

Model: `jinaai/jina-reranker-v3`

| Pipeline | Hit@1 | Hit@3 | Hit@5 |
|---|---:|---:|---:|
| Dense V1 | 31.6% | 42.1% | 63.2% |
| Hybrid + Reranker | **57.9%** | **68.4%** | **68.4%** |

Improvement over V1:
- Hit@1: +26.3 percentage points
- Hit@3: +26.3 percentage points
- Hit@5: +5.2 percentage points

### V2.5 Query Expansion
Status: **Completed, retained as optional fallback**

| Pipeline | Hit@1 | Hit@3 | Hit@5 |
|---|---:|---:|---:|
| Hybrid + Reranker | **57.9%** | 68.4% | 68.4% |
| + Query Expansion | 52.6% | **73.7%** | **73.7%** |

Query expansion improved Top-3/Top-5 coverage but reduced Top-1 precision and added another model call.

## Final V2 Default

```text
User Query
    ↓
Dense Retrieval ─────┐
                     ├── RRF
BM25 Retrieval ──────┘
       ↓
Hybrid Candidate Pool
       ↓
Jina Reranker
       ↓
Top 5
       ↓
Grounded LLM
```

**Default:** Hybrid + Reranker  
**Optional fallback:** Query expansion

## Status
PolicyIQ V2 retrieval optimization is frozen.
