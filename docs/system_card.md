# System Card

## System

AegisRAG 1.0 is a retrieval-augmented governance assistant and deterministic risk-screening prototype.

## Intended users

AI product teams, data scientists, governance analysts, auditors, and students working under qualified organisational oversight.

## Outputs

- Evidence-grounded answers with inline citation identifiers
- Source excerpts and official links
- Preliminary risk category and triggering factors
- Likely control areas, gaps, and recommended next actions
- Machine-readable JSON and human-readable Markdown reports

## Quality evidence

The committed ten-question offline evaluation achieved Recall@5 of 1.00, MRR of 1.00, citation coverage of 1.00, and answer-keyword coverage of 0.675. Sixteen automated tests cover ingestion, chunking, retrieval, guardrails, risk rules, orchestration, API behaviour, and audit logging.

## Safety behaviour

The system blocks common prompt-injection requests, redacts common PII patterns, uses only retrieved evidence in its generation prompt, sanitises citation identifiers, warns on provider failure, and abstains below a retrieval-confidence threshold.

## Known limitations

The rule engine cannot interpret all legal conditions and exceptions. The reference corpus is intentionally compact. The offline generator is extractive and less fluent than a hosted LLM. Citation presence does not by itself prove that every claim is entailed.

