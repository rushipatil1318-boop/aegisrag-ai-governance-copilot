# Threat Model

| Threat | Example | Current mitigation | Residual risk |
|---|---|---|---|
| User prompt injection | “Ignore previous instructions” | Input pattern detection and refusal | Novel or obfuscated attacks may pass |
| Indirect document injection | A source tells the model to leak context | System prompt treats retrieved text as untrusted evidence | Requires stronger content isolation in production |
| Hallucination | LLM invents an obligation | Evidence-only prompt, low temperature, citations, confidence gate | Citation may not fully entail a claim |
| Citation spoofing | LLM produces `[S99]` | Allowlist sanitisation | Valid citation can still be used imprecisely |
| PII leakage | Email or phone in a query | Pre-retrieval redaction | Pattern matching cannot identify every identifier |
| Corpus poisoning | Untrusted document added as authority | Curated source directory and metadata validation | Production ingestion needs signatures and approval workflow |
| Stale legal content | Regulation or guidance changes | Verification dates and official URLs | Requires scheduled re-verification |
| API secret exposure | Key committed to Git | Environment-only secrets and `.gitignore` | Runtime and platform configuration must remain secure |
| Denial of service | Extremely large prompt | Input length limit | API rate limiting is still needed in production |
| Audit-log disclosure | Logs reveal sensitive context | Logs store metadata rather than full prompts | Operational access control and retention are still required |

## Production hardening backlog

- Authentication, tenant isolation, rate limiting, and role-based access
- Signed source manifests and reviewer approval for ingestion
- Dedicated secrets manager and encrypted audit storage
- Automated legal-source freshness checks
- Stronger PII detection and policy-based retention
- LLM red-team suite and citation-entailment model
- Observability with privacy-safe metrics and incident alerts

