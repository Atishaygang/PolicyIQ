# PolicyIQ V2 Retrieval Architecture

## Final Default Architecture

```text
                         USER QUERY
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
         Dense Retriever             BM25 Retriever
         semantic similarity         lexical matching
                │                         │
           Top-N chunks              Top-N chunks
                └────────────┬────────────┘
                             ▼
                   Reciprocal Rank Fusion
                             │
                             ▼
                    Hybrid Candidate Pool
                             │
                             ▼
                  jinaai/jina-reranker-v3
                             │
                             ▼
                           Top 5
                             │
                             ▼
                     Grounded RAG Prompt
                             │
                             ▼
                            LLM
                             │
                             ▼
                  Answer + Source Citations
```

## Dense Retrieval
Uses the frozen V1 embedding + Chroma setup for semantic similarity.

## BM25 Retrieval
Operates on the same frozen chunks and captures exact policy terminology.

## Fusion
RRF combines rankings rather than raw dense/BM25 scores because the score scales are different.

## Deduplication
Fusion is performed at chunk level. Duplicate document/page results are removed after ranking so repeated page chunks do not waste final slots.

## Reranking
`jinaai/jina-reranker-v3` reranks hybrid candidates against the original user query.

## Optional Query Expansion
The original query is always retained. Two rewrites can be added, each run through hybrid retrieval, then fused and reranked once. This remains optional because it improved Hit@3/Hit@5 but reduced Hit@1.

## Frozen Components
- Corpus
- Cleaning
- Metadata generation
- Chunking 1200/200
- Embedding model
- Chroma
- Prompt
- LLM
- Golden questions
