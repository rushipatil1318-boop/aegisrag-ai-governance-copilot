from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean

from .citations import citation_coverage
from .orchestrator import AegisRAG


@dataclass(frozen=True)
class EvaluationRow:
    question_id: str
    question: str
    recall_at_k: float
    reciprocal_rank: float
    answer_keyword_coverage: float
    citation_coverage: float
    confidence: float
    latency_ms: float
    retrieved_sources: list[str]


def _keyword_coverage(text: str, keywords: list[str]) -> float:
    if not keywords:
        return 1.0
    normalized = text.lower()
    return sum(keyword.lower() in normalized for keyword in keywords) / len(keywords)


def evaluate(rag: AegisRAG, dataset_path: Path | None = None) -> tuple[dict, list[EvaluationRow]]:
    path = dataset_path or rag.settings.evaluation_path
    examples = json.loads(path.read_text(encoding="utf-8"))
    rows: list[EvaluationRow] = []
    for example in examples:
        hits = rag.retriever.search(
            rag._expand(example["question"]), top_k=rag.settings.top_k
        )
        retrieved = [hit.chunk.source_id for hit in hits]
        expected = set(example["expected_source_ids"])
        matched = expected & set(retrieved)
        recall = len(matched) / len(expected) if expected else 1.0
        ranks = [retrieved.index(source_id) + 1 for source_id in expected if source_id in retrieved]
        reciprocal_rank = 1 / min(ranks) if ranks else 0.0
        answer = rag.ask(example["question"])
        rows.append(
            EvaluationRow(
                question_id=example["id"],
                question=example["question"],
                recall_at_k=round(recall, 4),
                reciprocal_rank=round(reciprocal_rank, 4),
                answer_keyword_coverage=round(
                    _keyword_coverage(answer.answer, example.get("expected_keywords", [])), 4
                ),
                citation_coverage=round(citation_coverage(answer.answer), 4),
                confidence=answer.confidence,
                latency_ms=answer.latency_ms,
                retrieved_sources=retrieved,
            )
        )

    summary = {
        "examples": len(rows),
        "retrieval_recall_at_k": round(mean(row.recall_at_k for row in rows), 4),
        "mean_reciprocal_rank": round(mean(row.reciprocal_rank for row in rows), 4),
        "answer_keyword_coverage": round(mean(row.answer_keyword_coverage for row in rows), 4),
        "citation_coverage": round(mean(row.citation_coverage for row in rows), 4),
        "average_confidence": round(mean(row.confidence for row in rows), 4),
        "average_latency_ms": round(mean(row.latency_ms for row in rows), 2),
        "provider": rag.generator.provider_name,
        "embedding_backend": rag.retriever.embedding_backend.name,
    }
    return summary, rows


def rows_as_dicts(rows: list[EvaluationRow]) -> list[dict]:
    return [asdict(row) for row in rows]

