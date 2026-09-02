# ADR 002 — Text Splitting Strategy

> **Status:** Accepted  
> **Decision:** Recursive character splitting, `1200 / 200`  
> **Project:** PolicyIQ V1

---

## Context

Insurance PDFs contain definitions, exclusions, tables, policy conditions, regulatory clauses, and long legal paragraphs. Chunking must preserve evidence while limiting redundancy and maintaining page-level provenance.

## Decision

Use `RecursiveCharacterTextSplitter` with:

```text
chunk_size    = 1200
chunk_overlap = 200
length        = characters
```

Separator hierarchy:

```python
["\n\n", "\n", ". ", " ", ""]
```

Pages are cleaned first and remain separate before splitting, so chunks do not intentionally cross PDF page boundaries.

## Experiment A — 1000 / 150

```text
Total chunks: 1,319
Average chars: 836.79
Median chars: 943
Chunks < 200 chars: 28
```

Observed issues included more small fragments, an awkward AYUSH-definition split, fragmented depreciation tables, and more clause fragmentation.

## Experiment B — 1200 / 200

Final result after the cleaning fix:

```text
Total chunks: 1,144
Average characters: 979.05
Median characters: 1,139
Minimum characters: 74
Maximum characters: 1,199
Chunks under 200 chars: 13
```

This reduced fragmentation without making chunks excessively large.

## Golden Evidence Validation

The decision was not frozen from statistics alone. Every answerable golden question was manually checked for evidence preservation.

```text
Answerable questions: 19
PASS: 19
PARTIAL: 0
FAIL: 0
Full evidence coverage: 100%
```

## Page-Boundary Choice

Keeping chunks within source pages gives:

- Simple and precise citations.
- Easy golden evidence comparison.
- Strong provenance.

Trade-off: some concepts span pages and may require multiple chunks.

## Overlap Choice

`200` characters of overlap reduce boundary loss. Excessive overlap would create redundant vectors, duplicate top-k results, larger context windows, and additional embedding cost. This is a redundancy issue—not “overtraining.”

## Limitations

- Recursive splitting is not semantic understanding.
- Tables are not structurally reconstructed.
- Cross-page concepts can still be fragmented.

## Future Work

- Section-aware splitting.
- Table-aware parsing.
- Parent-child retrieval.
- Semantic chunking.
- Cross-page windows where provenance can remain explicit.

## Final Decision

**PolicyIQ V1 freezes recursive character splitting at `1200 / 200` as its evidence-validated baseline.**
