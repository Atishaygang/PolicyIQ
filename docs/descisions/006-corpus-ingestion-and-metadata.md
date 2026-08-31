# PolicyIQ Ingestion Pipeline

This module is responsible for converting the raw insurance PDF knowledge base into a clean, validated, metadata-rich collection of LangChain `Document` objects.

## Purpose

The ingestion pipeline prepares documents before chunking, embeddings, vector storage, retrieval, and answer generation.

Current flow:

```text
data/raw/
    ↓
discover all PDFs
    ↓
validate against manifest.csv
    ↓
process each PDF independently
    ↓
load page-wise
    ↓
detect repeated boilerplate
    ↓
clean page content
    ↓
attach business metadata
    ↓
drop empty pages
    ↓
combine into page-level corpus
    ↓
List[Document]


src/ingestion/
├── loader.py
├── cleaner.py
├── corpus.py
└── README.md