# ADR 004 — LLM Provider and Generation Model

> **Status:** Accepted  
> **Decision:** Hugging Face endpoint + `openai/gpt-oss-120b`  
> **Project:** PolicyIQ V1

---

## Context

After retrieval, PolicyIQ needs an LLM that can synthesize answers from supplied insurance evidence, cite source blocks, avoid unsupported claim conclusions, and abstain when context is insufficient.

## Decision

Use:

```text
HuggingFaceEndpoint
      ↓
ChatHuggingFace
      ↓
openai/gpt-oss-120b
```

Secrets are loaded from `.env` and must not be committed. `.env.example` documents required configuration.

## Generation Configuration

```text
temperature = 0
```

PolicyIQ is an evidence-grounded assistant, so deterministic, precise generation is preferred over creative variation.

## Prompting Strategy

The system prompt requires the model to:

- Use only supplied document context.
- Avoid invented policy terms, benefits, exclusions, limits, procedures, or claim decisions.
- Cite `[SOURCE N]` labels.
- Distinguish insurer policy wording from regulatory guidance.
- Avoid combining different policies/coverage sections into one universal rule.
- Abstain when context is insufficient.

Retrieved chunks are wrapped with explicit metadata:

```text
[SOURCE 1]
Document ID: ...
Filename: ...
PDF Page: ...
Content:
...
```

This reduces citation hallucination because the source identity is supplied by the pipeline.

## Grounding Improvement

An early intoxication answer overgeneralized a specific death/bodily-injury clause into a broad exclusion. The prompt was tightened to prohibit extending a clause beyond the policy section, coverage type, person, or benefit actually supported by the retrieved text.

After the change, the model correctly stated when vehicle-damage coverage could not be determined from the supplied excerpts.

## End-to-End Manual Tests

### Exact
`What depreciation applies to plastic parts?`

Result: correct **50%** answer with multiple source citations.

### Semantic
`Will damage be covered if the driver was drunk?`

Result: avoided overgeneralization and stated that the supplied excerpts were insufficient to determine vehicle-damage coverage.

### Regulatory
`What obligations does an insurer have regarding policyholder grievances?`

Result: synthesized relevant policyholder-protection guidance with citations.

### Unanswerable
`What will HDFC ERGO's share price be next month?`

Result:

```text
I could not find sufficient information in the provided documents.
```

## Alternatives Considered

Gemini was considered, but the Hugging Face endpoint was already functioning and avoided unnecessary provider switching during V1.

## Consequences

### Positive
- Working grounded generation.
- Good instruction following in V1 tests.
- No need to host a large model locally.

### Trade-offs
- External service dependency.
- No structured-output guarantee yet.
- Final answer quality still depends on retrieval sufficiency.

## Future Work

- Pydantic structured responses.
- Provider/model comparison.
- Citation validation.
- Automated groundedness testing.
- Token and latency tracking.

## Final Decision

**PolicyIQ V1 uses `openai/gpt-oss-120b` via Hugging Face for grounded generation.**
