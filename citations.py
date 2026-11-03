from __future__ import annotations

import re

from .schemas import Citation, SearchHit


def build_citations(hits: list[SearchHit], max_excerpt_words: int = 55) -> list[Citation]:
    citations: list[Citation] = []
    seen_sources: set[str] = set()
    for hit in hits:
        if hit.chunk.source_id in seen_sources:
            continue
        seen_sources.add(hit.chunk.source_id)
        excerpt = " ".join(hit.chunk.content.split()[:max_excerpt_words]).strip()
        if len(hit.chunk.content.split()) > max_excerpt_words:
            excerpt += "…"
        citations.append(
            Citation(
                citation_id=f"S{len(citations) + 1}",
                source_id=hit.chunk.source_id,
                title=hit.chunk.title,
                reference=hit.chunk.reference,
                source_url=hit.chunk.source_url,
                excerpt=excerpt,
                relevance=round(hit.score, 4),
            )
        )
    return citations


def sanitize_citations(text: str, citations: list[Citation]) -> str:
    allowed = {citation.citation_id for citation in citations}

    def replace(match: re.Match[str]) -> str:
        citation_id = match.group(1)
        return match.group(0) if citation_id in allowed else ""

    cleaned = re.sub(r"\[(S\d+)\]", replace, text)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    if citations and not re.search(r"\[S\d+\]", cleaned):
        cleaned += f" [{citations[0].citation_id}]"
    return cleaned


def citation_coverage(text: str) -> float:
    bullet_claims = [line.strip() for line in text.splitlines() if line.strip().startswith("-")]
    if bullet_claims:
        return sum(bool(re.search(r"\[S\d+\]", claim)) for claim in bullet_claims) / len(
            bullet_claims
        )
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence]
    factual = [sentence for sentence in sentences if len(sentence.split()) >= 7]
    if not factual:
        return 1.0
    cited = sum(bool(re.search(r"\[S\d+\]", sentence)) for sentence in factual)
    return cited / len(factual)

