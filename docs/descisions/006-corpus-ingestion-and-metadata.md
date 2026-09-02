# ADR 006 — Corpus Ingestion and Metadata Design

> **Status:** Accepted  
> **Decision:** Page-level ingestion + manifest-driven metadata  
> **Project:** PolicyIQ V1

---

## Context

RAG requires source identity, not just text. Every chunk must remain traceable to its PDF, page, product, category, and issuer for citations, evaluation, filtering, and debugging.

## Decision

Use:

1. `PyMuPDFLoader` for page-level extraction.
2. A manifest CSV for controlled business metadata.
3. Stable internal document IDs (`DOC001` … `DOC011`).
4. Metadata enrichment before chunking.

## Corpus Snapshot

```text
PDFs: 11
Raw PDF pages: 431
Usable cleaned page documents: 430
```

The corpus spans motor policies, health policy wording, IRDAI regulations, master circulars, FAQ content, and motor-service-provider guidance.

## Manifest Fields

```text
document_id
filename
document_type
issuer
insurer
product
year
category
source_url
```

The manifest is the authoritative catalog connecting files to business metadata.

## Stable IDs

Stable `DOCxxx` identifiers remain consistent even if filenames change. This supports reproducible logs, evaluation records, and future APIs.

## Page Convention

PyMuPDF uses zero-indexed `metadata["page"]`. PolicyIQ adds:

```text
pdf_page = page + 1
```

so citations match the human-visible PDF page.

## Ingestion Flow

```text
data/raw/
   ↓
recursive PDF discovery
   ↓
manifest validation
   ↓
load each PDF independently
   ↓
find repeated lines
   ↓
clean pages
   ↓
drop empty pages
   ↓
metadata enrichment
   ↓
combined corpus
```

## Validation Rules

The loader checks:

- Required manifest columns.
- Duplicate filenames.
- Duplicate document IDs.
- PDFs without manifest rows.
- Manifest rows without matching PDFs.
- Reserved metadata collisions.

Reserved fields include `page`, `pdf_page`, `source`, `file_path`, and `total_pages`.

## Why Page-Level Loading

### Benefits
- Precise citations.
- Easy evidence inspection.
- Straightforward golden dataset alignment.

### Trade-off
Some concepts span pages and may require multiple chunks.

## Future Work

- Document hashes/versioning.
- Effective dates.
- Jurisdiction metadata.
- Automatic manifest helpers.
- Better page-range provenance.

## Final Decision

**PolicyIQ V1 uses page-level PDF ingestion with stable document IDs and manifest-driven metadata enrichment.**
