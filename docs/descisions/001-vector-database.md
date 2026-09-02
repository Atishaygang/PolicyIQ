# ADR 001 — Vector Database Selection

> **Status:** Accepted  
> **Decision:** ChromaDB  
> **Project:** PolicyIQ V1  
> **Scope:** Dense vector storage and semantic retrieval

---

## Context

PolicyIQ requires a vector store for embeddings generated from cleaned and chunked insurance documents. The V1 corpus contains **11 insurance/regulatory PDFs**, **430 usable page documents**, and **1,144 final chunks**. The priority is a local, inspectable, reproducible baseline rather than distributed infrastructure.

## Decision

Use **ChromaDB** with local persistence.

```text
Collection: policyiq_v1
Stored vectors: 1,144
Embedding dimension: 384
Persistence: local disk
```

Index construction and querying are deliberately separated:

```text
build_vector_store.py
  → load corpus
  → split documents
  → embed chunks
  → create/populate Chroma

query_vector_store.py
  → open existing collection
  → similarity search
```

## Why Chroma

- Local persistence.
- Simple LangChain integration.
- Metadata support on each chunk.
- Low operational overhead.
- Easy rebuild/debug cycle.
- Sufficient for the current corpus size.

Chunk metadata includes provenance such as `document_id`, `filename`, `document_type`, `issuer`, `insurer`, `product`, `category`, and `pdf_page`.

## Alternatives Considered

### FAISS
Fast and lightweight, but less convenient for the current persistence + metadata workflow.

### Pinecone
Production-ready managed vector infrastructure, but unnecessary external complexity for V1.

### Qdrant
Strong filtering and production features, but more operational overhead than the current baseline requires.

## Important Failure Discovered

Repeated use of `from_documents(...)` against the same persistent collection inserted the same 1,144 chunks multiple times.

```text
Expected: 1,144
Observed: 4,576
```

The store was deleted, rebuilt once, and the codebase was split into build and query paths. A clean V1 index now contains exactly **1,144 vectors**.

## Consequences

### Positive
- Reproducible local retrieval.
- Persistent embeddings.
- Metadata and provenance remain attached to chunks.
- Easy evaluation and debugging.

### Trade-offs
- Local configuration is not a large-scale production architecture.
- V1 uses dense retrieval only.
- Future migration may be needed if scale or filtering requirements increase.

## Validation

Validated through vector-count checks, semantic retrieval tests, golden-question diagnostics, and end-to-end RAG generation.

## Future Work

- Metadata filtering.
- Hybrid retrieval.
- Reranking.
- Query rewriting.
- Deliberate migration to newer vector integrations when justified.

## Final Decision

**ChromaDB is accepted as the PolicyIQ V1 vector-store baseline.**
