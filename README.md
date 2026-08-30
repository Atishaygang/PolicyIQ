# PolicyIQ

Enterprise Insurance Policy & Claims Intelligence using RAG.

## Problem

Insurance professionals often need to search across lengthy policy,
endorsement, claims and regulatory documents to answer coverage-related
questions.

PolicyIQ aims to retrieve relevant evidence and generate grounded answers
with source citations.

## Current Stage

V0 — Foundation

# PolicyIQ

Enterprise Insurance Policy & Claims Intelligence using
Retrieval-Augmented Generation.

## Problem

Insurance professionals frequently need to retrieve information from
large policy documents, endorsements, claims guidelines and regulatory
documents.

Traditional keyword search may fail when the user's wording differs from
the terminology used in the documents.

PolicyIQ aims to build a grounded RAG system capable of retrieving
relevant insurance evidence and generating answers with document/page
citations.

## Project Roadmap

- [x] V0 — Foundation
- [ ] V1 — Core RAG
- [ ] V2 — Retrieval Optimization
- [ ] V3 — Advanced/Hybrid RAG
- [ ] V4 — Evaluation
- [ ] V5 — Production API
- [ ] V6 — Agentic AI / LangGraph

## V0 — Completed

- Project repository initialized
- Python environment configured
- Insurance document corpus collected
- Document manifest created
- Golden evaluation dataset created
- Configuration structure established
- Initial architecture decisions documented

## Current Stage

**V1 — Core RAG**

Next:

Documents → Loading → Chunking → Embeddings → Chroma →
Retriever → LLM → Grounded Answer + Citations