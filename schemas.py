from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    title: str
    content: str
    framework: str
    reference: str
    source_url: str
    last_verified: str
    topics: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source_id: str
    title: str
    section: str
    content: str
    framework: str
    reference: str
    source_url: str
    topics: tuple[str, ...] = ()


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float
    lexical_score: float
    semantic_score: float
    rerank_score: float
    rank: int

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data


@dataclass(frozen=True)
class Citation:
    citation_id: str
    source_id: str
    title: str
    reference: str
    source_url: str
    excerpt: str
    relevance: float


@dataclass
class Answer:
    query: str
    answer: str
    intent: str
    confidence: float
    citations: list[Citation]
    evidence_quality: str
    warnings: list[str]
    latency_ms: float
    provider: str
    trace_id: str
    refused: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RiskAssessment:
    system_name: str
    risk_level: str
    confidence: float
    triggers: list[str]
    likely_obligations: list[str]
    control_gaps: list[str]
    recommended_actions: list[str]
    citations: list[Citation]
    disclaimer: str
    trace_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

