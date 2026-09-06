# PolicyIQ V2 Release Notes

## Goal
Improve retrieval quality without breaking the V1 grounded RAG system.

## Added
- BM25 lexical retrieval
- Hybrid dense + BM25 retrieval
- Reciprocal Rank Fusion
- Post-ranking deduplication
- Jina reranking
- Query expansion experiment
- Multi-query fusion
- Cached BM25 construction
- Cached reranker loading
- Retrieval evaluation scripts

## Selected V2 Default

```text
User Query
    ↓
Dense Retrieval ─────┐
                     ├── RRF
BM25 Retrieval ──────┘
       ↓
Hybrid Candidates
       ↓
Jina Reranker
       ↓
Top 5
       ↓
Grounded LLM
```

## Metrics

V1 Dense:
- Hit@1 31.6%
- Hit@3 42.1%
- Hit@5 63.2%

Selected V2:
- Hit@1 57.9%
- Hit@3 68.4%
- Hit@5 68.4%

Query expansion experiment:
- Hit@1 52.6%
- Hit@3 73.7%
- Hit@5 73.7%

## Freeze Decision
PolicyIQ V2 retrieval optimization is complete and frozen. The next phase should evaluate complete RAG answer quality: correctness, groundedness, completeness, citation accuracy, and abstention.
