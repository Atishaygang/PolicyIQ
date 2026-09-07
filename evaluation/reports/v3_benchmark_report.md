PolicyIQ V3 Benchmark Report

1. Objective

PolicyIQ V3 evaluates whether the system can consistently produce correct, grounded, cited answers from retrieved insurance evidence and refuse when evidence is insufficient.

V3 keeps the V2 retrieval stack frozen and evaluates the end-to-end RAG behavior across answer quality, grounding, citations, refusal behavior, latency, and failure modes.

2. Frozen System Under Evaluation

Retrieval path

User Query
→ Dense Retrieval + BM25
→ Reciprocal Rank Fusion (RRF)
→ Jina Reranker
→ Top-5 Evidence
→ Grounded Prompt
→ LLM
→ Answer + Citations

Important constraint: Retrieval configuration was not modified during V3 evaluation.

3. Evaluation Dataset

Total questions: 24

Answerable questions: 19

Unanswerable questions: 5

Evaluation categories included:

Exact retrieval

Semantic / paraphrased retrieval

Multi-document reasoning

Unanswerable questions

The same golden evaluation set was retained so V3 remains comparable with earlier retrieval experiments.

4. V3 Evaluation Outputs

The complete end-to-end baseline was saved as:

evaluation/rag_runs/v3_baseline.json

Manual evaluation scores were saved as:

evaluation/reports/v3_manual_scores.json

Latency analysis was saved as:

evaluation/reports/v3_latency_report.json

Failure analysis was saved as:

evaluation/reports/v3_failure_analysis.json

5. Manual Evaluation Results

5.1 Faithfulness

Mean faithfulness: 1.75 / 2

Interpretation:

Most generated answers were grounded in the retrieved evidence.

A small number of responses contained partial interpretation or evidence-usage issues.

The largest generation-side failure was Q008, where relevant intoxication wording was present in retrieved evidence but the answer still concluded that the available information was insufficient.

5.2 Answer Relevance

Mean answer relevance: 1.368 / 2

Interpretation:

Many answers were direct and complete.

Some answers were incomplete, indirect, or answered a nearby information need rather than the exact one asked.

False refusals significantly reduced the relevance score.

5.3 Citation Correctness

PASS: 13

PARTIAL: 3

Interpretation:

Most citations that were provided supported the factual claims attached to them.

Partial cases mainly involved:

correct overall conclusions with incomplete source coverage

claims that were only partially supported by the cited chunk

responses that relied on inference rather than directly cited evidence

5.4 Citation Completeness

PASS: 12

PARTIAL: 4

Interpretation:

PolicyIQ usually cited the important factual claims, but some answers contained additional claims that were not fully covered by the cited evidence.

6. Refusal Evaluation

Correct refusals on unanswerable questions

5 / 5

PolicyIQ correctly refused all intentionally unanswerable questions.

This shows strong hallucination resistance for cases such as:

future claim approval

exact future payout

exact future premium increase

fastest nearby garage

probability of future IRDAI rule changes

False refusals on answerable questions

4

False-refusal questions:

Q003

Q004

Q008

Q018

This is the most important weakness identified in V3.

7. Latency Results

Metric

Result

Average latency

104.93 s

Median latency

99.97 s

P95 latency

163.27 s

Minimum latency

68.40 s

Maximum latency

166.20 s

Interpretation

The current pipeline is suitable for offline evaluation and experimentation but is not production-ready from a serving-latency perspective.

The dominant runtime cost comes from the retrieval/reranking/generation stack operating on CPU and remote model inference.

Latency optimization was intentionally not performed during V3 because this version focused on measurement and reliability analysis.

8. Failure Analysis

Overall classification

Failure Type

Count

Retrieval failure

3

Generation / interpretation failure

1

Citation / evidence-usage issue

3

Answer completeness issue

2

No material failure

15

High-severity failures

Q003

Q004

Q008

Q018

Medium-severity failures

Q009

Q011

Q015

Q016

Q019

9. High-Severity Failure Breakdown

Q003 — Retrieval Failure

Question: Emergency hospitalization notification timeline.

Failure: The required policy evidence did not reach the final Top-5 context.

Observed behavior: PolicyIQ refused to answer.

Root cause: Retrieval/ranking failure rather than hallucination.

Q004 — Retrieval Failure

Question: Free-look period for a new individual Optima Secure policy.

Failure: The expected free-look clause was not retrieved in the final evidence set.

Observed behavior: PolicyIQ refused.

Root cause: Retrieval/ranking failure.

Q008 — Generation / Interpretation Failure

Question: Whether own-damage loss is covered when the driver was drunk.

Failure: Relevant intoxication wording was present in retrieved motor-policy evidence, but the model concluded that the context was insufficient.

Observed behavior: False refusal.

Root cause: Generation-layer interpretation failure.

Importance: This is the clearest example in V3 where retrieval succeeded but generation still failed.

Q018 — Retrieval Failure

Question: Planned hospitalization notice plus broader IRDAI claim-handling duty.

Failure: The final Top-5 evidence did not contain the necessary policy-notification clause and corresponding regulatory evidence.

Observed behavior: PolicyIQ refused.

Root cause: Retrieval/ranking failure.

10. Medium-Severity Failure Breakdown

Q009 — Citation Completeness Issue

The final conclusion was correct, but citation support was stronger for police notification than for insurer notification.

Q011 — Evidence Usage / Completeness Issue

The answer was directionally correct, but it reasoned from the absence of a prohibition instead of clearly using the retrieved reimbursement-claim pathway.

Q015 — Citation / Evidence Completeness Issue

The intended conclusion was correct, but the decisive FAQ sentence was truncated in the retrieved context, so the answer relied partly on inference.

Q016 — Answer Completeness Issue

The response correctly discussed loss notification and surveyor handling but did not fully address the exact IRDAI claim-document governance requirement expected by the evaluation.

Q019 — Answer Completeness Issue

The HDFC ERGO deductible explanation was grounded, but the IRDAI portion answered a Customer Information Sheet disclosure requirement rather than the exact intended deductible definition.

11. Key Findings

Strengths

Strong hallucination resistance

PolicyIQ correctly refused all 5 intentionally unanswerable questions.

High grounding quality

Mean faithfulness of 1.75 / 2 indicates that most factual claims were supported by retrieved evidence.

Generally reliable citations

Most citation checks passed.

Citation failures were mostly completeness or evidence-usage problems rather than fabricated sources.

Good performance on direct regulatory and policy clauses

Exact factual questions with clearly retrieved evidence were usually answered correctly.

Multi-document reasoning works when both required evidence pieces are retrieved

Q017 is a strong example of successful synthesis across insurer policy wording and IRDAI regulation.

12. Main Weaknesses

1. Retrieval remains the dominant high-severity failure source

Three of the four high-severity failures were caused by relevant evidence not reaching the final Top-5 context.

This means retrieval quality remains the most important technical reliability bottleneck.

2. Over-refusal exists

The refusal prompt is conservative, which protects against hallucination, but the system sometimes refuses answerable questions.

This creates a trade-off:

Lower hallucination risk ↔ Higher false-refusal risk

3. Generation can still misinterpret correct evidence

Q008 demonstrates that even when relevant evidence is retrieved, the LLM can fail to interpret the clause correctly.

4. Some answers are grounded but not fully aligned with the exact information need

Several medium-severity questions were factually grounded but incomplete, indirect, or focused on a nearby clause.

5. Latency is too high for production use

Median latency is approximately 100 seconds, so serving optimization would be necessary before deployment.

13. Final V3 Assessment

PolicyIQ is no longer just a technically functioning RAG demo.

The V3 evaluation shows that the system has:

strong grounding behavior

strong refusal behavior on genuinely unanswerable questions

generally correct citation usage

useful multi-document reasoning capability

measurable and explainable failure modes

However, it is not yet fully reliable.

The biggest current reliability issue is not hallucination. It is missing or misusing evidence, particularly:

relevant evidence failing to reach Top-5

false refusals caused by retrieval misses

occasional generation misinterpretation even when evidence is present

The current system should therefore be described as:

A grounded insurance RAG system with strong hallucination resistance and good citation discipline, but with remaining retrieval recall, interpretation, and latency limitations.

14. V3 Conclusion

V3 successfully answered the core evaluation question:

Can PolicyIQ consistently produce correct, grounded, cited answers from evidence and refuse when evidence is insufficient?

Result: Mostly yes, but not consistently enough for production-grade reliability yet.

The system performs well when the correct evidence reaches the generation layer. The dominant remaining challenge is ensuring that the right evidence reliably survives retrieval and ranking into the final context.

15. Version Status

V3 — End-to-End RAG Evaluation

Status: Complete

Completed components:

Frozen evaluation dataset

Complete RAG trace capture

Manual citation evaluation

Manual faithfulness evaluation

Manual answer-relevance evaluation

Refusal evaluation

Latency measurement

Failure classification

Final benchmark report