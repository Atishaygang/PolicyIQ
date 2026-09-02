# ADR 005 — Document Cleaning Strategy

> **Status:** Accepted  
> **Decision:** Conservative, document-local, two-stage cleaning  
> **Project:** PolicyIQ V1

---

## Context

Insurance PDFs contain repeated headers, footers, page numbers, page labels, and formatting artifacts. Embedding these repeatedly would create low-value vectors, but aggressive cleaning could remove meaningful clause numbers, deductibles, percentages, dates, or limits.

## Decision

Clean each PDF independently and conservatively.

```text
Stage 1
  → normalize line artifacts
  → remove blanks
  → remove repeated document-local boilerplate

Stage 2
  → recalculate line boundaries
  → remove matching standalone page numbers near boundaries
  → remove dynamic page-label patterns near boundaries
```

## Why Document-Local Detection

A phrase repeated across different policies may still be meaningful. Boilerplate is therefore detected within each PDF, not across the entire corpus.

## Repeated-Line Detection

For each page, unique non-empty lines are counted. Using a set per page prevents one line repeated several times on one page from inflating its frequency.

Current threshold:

```text
0.6
```

A line does not need to appear on 100% of pages because cover/special pages may differ.

## Page-Number Safety

PolicyIQ intentionally avoids generic rules such as `isdigit()` because numeric text can be genuine insurance evidence.

A number is removed only when it:

1. Appears near a page boundary.
2. Matches the actual PDF page number.

## Important Bug and Fix

Originally, boundary checks were calculated before repeated headers were removed. A page number could therefore sit outside the first/last boundary window in raw text, then become the first line after header removal and survive cleaning.

The two-stage cleaner fixed this ordering problem by recalculating boundaries after boilerplate removal.

## Raw vs Clean Documents

The loader preserves both `raw_docs` and `clean_docs` to support auditability, debugging, and before/after inspection.

## Empty Pages

One genuinely empty page was identified in the corpus and excluded from useful downstream processing.

## Validation

Cleaning was validated through page inspection, chunk inspection, and golden evidence coverage. All **19 answerable questions** retained sufficient evidence after cleaning and chunking.

## Future Work

- Layout-aware parsing.
- Better table extraction.
- OCR fallback for scanned PDFs.
- Section reconstruction.

## Final Decision

**PolicyIQ V1 uses conservative, document-local, two-stage cleaning with evidence preservation as the primary constraint.**
