# ADR 010 — Do Not Use Hard Metadata Filtering by Default

## Status
Rejected as default

## Context
The corpus contains overlapping metadata categories such as motor, health, regulatory, and claims_and_servicing. Some valid questions require evidence across categories.

## Experiment
A controlled query was run with and without a hard metadata category filter. The ranking did not improve.

## Decision
Do not apply hard metadata filtering by default.

## Retained Uses
Metadata remains useful for provenance, citations, debugging, evaluation, analytics, future routing, and optional user-controlled filters.
