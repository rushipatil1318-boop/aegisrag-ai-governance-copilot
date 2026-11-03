from __future__ import annotations

import time
import uuid
from collections import Counter
from typing import Any

from .chunking import chunk_documents
from .citations import build_citations, sanitize_citations
from .config import Settings
from .config import settings as default_settings
from .documents import load_documents
from .embeddings import create_embedding_backend
from .guardrails import inspect_input, inspect_output
from .llm import OfflineEvidenceGenerator, create_generator
from .retrieval import HybridRetriever
from .risk import assess_system
from .schemas import Answer, Citation, RiskAssessment
from .telemetry import AuditLogger

INTENT_KEYWORDS = {
    "risk_classification": {"risk", "classified", "classification", "high-risk", "prohibited"},
    "obligations": {"must", "obligation", "requirement", "required", "comply", "article"},
    "controls": {"control", "governance", "monitor", "measure", "mitigate", "oversight"},
    "transparency": {"transparent", "transparency", "chatbot", "disclose", "generated"},
}

QUERY_EXPANSIONS = {
    "bias": "data governance representativeness discrimination fairness",
    "hiring": "employment recruitment candidate ranking Annex III high-risk",
    "chatbot": "direct interaction natural persons transparency Article 50",
    "logs": "automatic recording events record keeping traceability Article 12",
    "security": "accuracy robustness cybersecurity Article 15",
    "impact assessment": "fundamental rights impact assessment deployer Article 27",
    "respond": "NIST MANAGE prioritise mitigate residual risk action owner monitor",
    "measuring": "NIST MANAGE prioritise mitigate residual risk action owner monitor",
}


class AegisRAG:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or default_settings
        self.documents = load_documents(self.settings.knowledge_base_dir)
        self.chunks = chunk_documents(self.documents)
        backend = create_embedding_backend(
            self.settings.embedding_backend, self.settings.sentence_transformer_model
        )
        self.retriever = HybridRetriever(self.chunks, backend)
        self.generator = create_generator(self.settings)
        self.audit = AuditLogger(self.settings.audit_log_path)

    @staticmethod
    def _intent(query: str) -> str:
        tokens = set(query.lower().replace("?", "").split())
        scores = {
            intent: len(tokens & keywords) for intent, keywords in INTENT_KEYWORDS.items()
        }
        best = max(scores, key=scores.get)
        return best if scores[best] else "general_governance"

    @staticmethod
    def _expand(query: str) -> str:
        additions = [words for key, words in QUERY_EXPANSIONS.items() if key in query.lower()]
        return f"{query} {' '.join(additions)}".strip()

    @staticmethod
    def _confidence(hits: list) -> float:
        if not hits:
            return 0.0
        top = hits[0].score
        mean_top = sum(hit.score for hit in hits[:3]) / min(3, len(hits))
        diversity = len({hit.chunk.source_id for hit in hits}) / len(hits)
        return round(min(1.0, 0.55 * top + 0.25 * mean_top + 0.20 * diversity), 4)

    @staticmethod
    def _quality(confidence: float, citations: list[Citation]) -> str:
        if confidence >= 0.68 and len(citations) >= 2:
            return "high"
        if confidence >= 0.42 and citations:
            return "moderate"
        return "low"

    def ask(self, query: str, top_k: int | None = None) -> Answer:
        started = time.perf_counter()
        trace_id = uuid.uuid4().hex[:16]
        guardrail = inspect_input(query)
        if not guardrail.safe:
            result = Answer(
                query=guardrail.sanitized_text,
                answer=(
                    "I cannot process this request because it contains a prompt-injection pattern "
                    "or exceeds the input safety limits."
                ),
                intent="blocked",
                confidence=0.0,
                citations=[],
                evidence_quality="none",
                warnings=guardrail.warnings,
                latency_ms=round((time.perf_counter() - started) * 1000, 2),
                provider=self.generator.provider_name,
                trace_id=trace_id,
                refused=True,
            )
            self.audit.write("query_blocked", trace_id, {"warnings": result.warnings})
            return result

        sanitized_query = guardrail.sanitized_text
        intent = self._intent(sanitized_query)
        hits = self.retriever.search(
            self._expand(sanitized_query), top_k=top_k or self.settings.top_k
        )
        confidence = self._confidence(hits)
        citations = build_citations(hits)
        warnings = list(guardrail.warnings)

        if confidence < self.settings.min_confidence:
            answer_text = (
                "The current knowledge base does not contain enough relevant evidence to answer "
                "this reliably. Review the linked official sources or add authoritative documents."
            )
            warnings.append("Answer abstained because retrieval confidence was below threshold.")
            refused = True
        else:
            try:
                answer_text = self.generator.generate(sanitized_query, hits, citations)
                refused = False
            except Exception as exc:
                fallback = OfflineEvidenceGenerator()
                answer_text = fallback.generate(sanitized_query, hits, citations)
                warnings.append(
                    "Configured LLM was unavailable; used the offline evidence generator "
                    f"({type(exc).__name__})."
                )
                refused = False

        answer_text = sanitize_citations(answer_text, citations)
        warnings.extend(
            inspect_output(answer_text, {citation.citation_id for citation in citations})
        )
        result = Answer(
            query=sanitized_query,
            answer=answer_text,
            intent=intent,
            confidence=confidence,
            citations=citations,
            evidence_quality=self._quality(confidence, citations),
            warnings=list(dict.fromkeys(warnings)),
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
            provider=self.generator.provider_name,
            trace_id=trace_id,
            refused=refused,
        )
        self.audit.write(
            "answer_generated",
            trace_id,
            {
                "intent": intent,
                "confidence": confidence,
                "source_ids": [citation.source_id for citation in citations],
                "latency_ms": result.latency_ms,
                "provider": result.provider,
                "refused": result.refused,
            },
        )
        return result

    def assess(self, system: dict[str, Any]) -> RiskAssessment:
        trace_id = uuid.uuid4().hex[:16]
        name = str(system.get("system_name") or "Unnamed AI system")
        purpose_guard = inspect_input(str(system.get("purpose") or ""))
        safe_system = dict(system)
        safe_system["purpose"] = purpose_guard.sanitized_text
        decision = assess_system(safe_system)
        evidence_query = (
            f"{decision.risk_level} AI system requirements controls "
            f"{' '.join(decision.triggers)} {safe_system.get('purpose', '')}"
        )
        hits = self.retriever.search(evidence_query, top_k=self.settings.top_k)
        citations = build_citations(hits)
        result = RiskAssessment(
            system_name=name,
            risk_level=decision.risk_level,
            confidence=decision.confidence,
            triggers=decision.triggers,
            likely_obligations=decision.likely_obligations,
            control_gaps=decision.control_gaps,
            recommended_actions=decision.recommended_actions,
            citations=citations,
            disclaimer=(
                "Automated preliminary screening only. It is not legal advice or a conformity "
                "assessment. Validate against the complete current law and qualified reviewers."
            ),
            trace_id=trace_id,
        )
        self.audit.write(
            "risk_assessment",
            trace_id,
            {
                "system_name": name,
                "risk_level": result.risk_level,
                "confidence": result.confidence,
                "gap_count": len(result.control_gaps),
                "source_ids": [citation.source_id for citation in citations],
            },
        )
        return result

    def source_summary(self) -> dict[str, Any]:
        frameworks = Counter(document.framework for document in self.documents)
        return {
            "documents": len(self.documents),
            "chunks": len(self.chunks),
            "frameworks": dict(frameworks),
            "embedding_backend": self.retriever.embedding_backend.name,
            "llm_provider": self.generator.provider_name,
        }

