# Chunking Experiments

## Objective

Evaluate chunking strategies for the PolicyIQ insurance RAG system before creating embeddings.

The goal is not only to reduce the number of chunks, but to preserve complete insurance concepts, definitions, exclusions, clauses, and tables while retaining page-level metadata for citation.

---

# Experiment A

## Configuration

- Splitter: `RecursiveCharacterTextSplitter`
- Chunk size: `1000` characters
- Chunk overlap: `150` characters
- Length function: `len`
- Page crossing: Not allowed
- Input: cleaned page-level `Document` objects

Separators:

```python
[
    "\n\n",
    "\n",
    ". ",
    " ",
    ""
]
```

## Results

- Total chunks: 1319
- Average characters: 836.79
- Median characters: 943
- Minimum characters: 74
- Maximum characters: 1000
- Chunks under 200 characters: 28

## Chunks per document

- DOC010: 483
- DOC009: 15
- DOC004: 204
- DOC001: 69
- DOC002: 79
- DOC003: 90
- DOC011: 41
- DOC005: 156
- DOC006: 136
- DOC007: 30
- DOC008: 16

## Observations

### Positive

- Metadata was preserved after chunking.
- Page-level citation remained possible.
- Chunk overlap worked correctly.
- Most chunks were close to the configured maximum size.

### Problems observed

- Some logical units were fragmented.
- DOC001 depreciation schedule was split across multiple chunks.
- DOC004 AYUSH Hospital definition was fragmented, including a small continuation chunk.
- Regulatory clauses in DOC006 were occasionally divided across chunks.
- 28 chunks contained fewer than 200 characters.

## Conclusion

Experiment A worked as a reasonable baseline but showed unnecessary fragmentation in several important insurance concepts.

---

# Experiment B

## Configuration

- Splitter: `RecursiveCharacterTextSplitter`
- Chunk size: `1200` characters
- Chunk overlap: `200` characters
- Length function: `len`
- Page crossing: Not allowed
- Input: cleaned page-level `Document` objects

Separators:

```python
[
    "\n\n",
    "\n",
    ". ",
    " ",
    ""
]
```

## Initial Results

- Total chunks: 1145
- Average characters: 978.63
- Median characters: 1139
- Minimum characters: 74
- Maximum characters: 1199
- Chunks under 200 characters: 13

## Cleaning Issue Discovered

During manual inspection, standalone printed page numbers such as:

```text
1
2
3
```

were still present at the beginning of some HDFC policy pages.

The cleaner already attempted to remove page numbers only near document boundaries.

However, boundary detection was being calculated before repeated headers and boilerplate were removed.

Therefore, a printed page number could originally appear around line 10 and not be considered near the boundary. After repeated header removal, that same page number became the first line of the cleaned page.

## Cleaning Fix

Cleaning was changed into two stages:

1. Remove blank lines and repeated boilerplate.
2. Recalculate page boundaries and remove printed page numbers or page-label patterns.

This allowed standalone page numbers to be removed safely without deleting legitimate numeric clauses from the policy text.

---

# Experiment B — Final After Cleaning Fix

## Results

- Total chunks: 1144
- Average characters: 979.05
- Median characters: 1139
- Minimum characters: 74
- Maximum characters: 1199
- Chunks under 200 characters: 13

## Chunks per document

- DOC010: 432
- DOC009: 13
- DOC004: 174
- DOC001: 59
- DOC002: 66
- DOC003: 76
- DOC011: 32
- DOC005: 135
- DOC006: 117
- DOC007: 25
- DOC008: 15

## Manual Observations

### DOC001 — Motor Policy

The depreciation schedule is preserved much better than in Experiment A.

Most of the age-wise depreciation table now remains inside a single chunk rather than being fragmented into a separate small continuation chunk.

Exclusion clauses and intoxication-related wording are also retained with sufficient surrounding context.

### DOC004 — Health Policy

The AYUSH Hospital definition is substantially better preserved.

The definition text remains together within the same chunk up to the PDF page boundary.

However, some criteria continue onto the next PDF page.

This is not caused by chunk size because the system currently chunks page-level `Document` objects independently.

Therefore:

```text
chunk-size fragmentation
→ can be improved using larger chunks

PDF-page fragmentation
→ cannot be solved by increasing chunk size
```

This is currently accepted because retaining exact PDF-page metadata is important for citations and evaluation.

### DOC006 — IRDAI Regulation

Larger chunks preserve regulatory clauses and surrounding context better than Experiment A.

---

# Experiment Comparison

| Metric | Experiment A | Experiment B Final |
|---|---:|---:|
| Chunk Size | 1000 | 1200 |
| Overlap | 150 | 200 |
| Total Chunks | 1319 | 1144 |
| Average Characters | 836.79 | 979.05 |
| Median Characters | 943 | 1139 |
| Minimum Characters | 74 | 74 |
| Maximum Characters | 1000 | 1199 |
| Chunks < 200 chars | 28 | 13 |

## Interpretation

Experiment B produces fewer chunks while preserving more context.

It also reduces the number of very small chunks significantly.

The decision is not based only on the smaller chunk count. Manual inspection showed that important insurance definitions, depreciation schedules, exclusions, and regulatory clauses were generally more self-contained.

---

# Current Decision

Current preferred baseline:

```text
chunk_size = 1200
chunk_overlap = 200
```

Status:

```text
Cleaning baseline: Frozen
Chunking baseline: 1200 / 200
Total chunks: 1144
```

This configuration is not considered permanently optimal yet.

It will next be evaluated against the manually created golden evaluation dataset to determine whether the expected evidence for benchmark questions is sufficiently represented inside the produced chunks.

---

# Next Experiment

## Golden Evidence Coverage

For each answerable question in the golden evaluation dataset:

1. Identify the expected document.
2. Identify the expected page.
3. Inspect chunks generated from that page.
4. Determine whether at least one chunk contains sufficient evidence to answer the question.
5. Record failures caused by:
   - chunk boundaries
   - page boundaries
   - document extraction
   - missing context

Only after this validation will the chunking configuration be considered ready for the embedding stage.
