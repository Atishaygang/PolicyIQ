# ADR 007 — Use Hybrid Dense + BM25 Retrieval

## Status
Accepted

## Context
Dense retrieval captures semantic similarity but can miss exact insurance terminology. BM25 captures lexical matches but underperformed dense retrieval standalone.

## Decision
Use both dense retrieval and BM25, combined with Reciprocal Rank Fusion (RRF).

## Evidence
Dense V1: Hit@1 31.6%, Hit@3 42.1%, Hit@5 63.2%, Hit@15 73.7%.

Hybrid RRF: Hit@1 42.1%, Hit@3 52.6%, Hit@5 68.4%, Hit@15 84.2%.

## Consequences
Positive: stronger retrieval across measured cutoffs and complementary semantic/lexical coverage.  
Negative: additional index and retrieval complexity.

## Final Decision
Hybrid retrieval is part of the PolicyIQ V2 default pipeline.
