from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np

from .embeddings import EmbeddingBackend
from .schemas import Chunk, SearchHit

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def _minmax(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values
    low = float(values.min())
    high = float(values.max())
    if high - low < 1e-12:
        return np.zeros_like(values) if high == 0 else np.ones_like(values)
    return (values - low) / (high - low)


class BM25Index:
    def __init__(self, texts: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.documents = [tokenize(text) for text in texts]
        self.lengths = np.asarray([len(document) for document in self.documents], dtype=float)
        self.avg_length = float(self.lengths.mean()) if len(self.lengths) else 1.0
        self.term_counts = [Counter(document) for document in self.documents]
        document_frequency: Counter[str] = Counter()
        for document in self.documents:
            document_frequency.update(set(document))
        count = len(self.documents)
        self.idf = {
            term: math.log(1 + (count - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def score(self, query: str) -> np.ndarray:
        query_terms = tokenize(query)
        scores = np.zeros(len(self.documents), dtype=float)
        for index, frequencies in enumerate(self.term_counts):
            length_norm = 1 - self.b + self.b * self.lengths[index] / max(self.avg_length, 1.0)
            for term in query_terms:
                frequency = frequencies.get(term, 0)
                if not frequency:
                    continue
                numerator = frequency * (self.k1 + 1)
                denominator = frequency + self.k1 * length_norm
                scores[index] += self.idf.get(term, 0.0) * numerator / denominator
        return scores


class HybridRetriever:
    def __init__(
        self,
        chunks: list[Chunk],
        embedding_backend: EmbeddingBackend,
        lexical_weight: float = 0.52,
        semantic_weight: float = 0.48,
    ) -> None:
        if not chunks:
            raise ValueError("At least one chunk is required")
        self.chunks = chunks
        self.embedding_backend = embedding_backend
        self.lexical_weight = lexical_weight
        self.semantic_weight = semantic_weight
        texts = [self._search_text(chunk) for chunk in chunks]
        self.bm25 = BM25Index(texts)
        self.document_vectors = embedding_backend.fit(texts)

    @staticmethod
    def _search_text(chunk: Chunk) -> str:
        topics = " ".join(chunk.topics)
        return f"{chunk.title} {chunk.section} {chunk.reference} {topics} {chunk.content}"

    @staticmethod
    def _rerank_bonus(query: str, chunk: Chunk) -> float:
        query_tokens = set(tokenize(query))
        title_tokens = set(tokenize(f"{chunk.title} {chunk.section} {' '.join(chunk.topics)}"))
        coverage = len(query_tokens & title_tokens) / max(len(query_tokens), 1)
        article_matches = set(re.findall(r"article\s+(\d+)", query.lower()))
        reference_matches = set(re.findall(r"article\s+(\d+)", chunk.reference.lower()))
        article_bonus = 0.2 if article_matches & reference_matches else 0.0
        official_bonus = 0.04 if chunk.framework in {"EU AI Act", "NIST AI RMF"} else 0.0
        return min(1.0, 0.65 * coverage + article_bonus + official_bonus)

    def search(self, query: str, top_k: int = 5) -> list[SearchHit]:
        lexical_raw = self.bm25.score(query)
        query_vector = self.embedding_backend.encode_query(query)
        semantic_raw = np.asarray(self.document_vectors @ query_vector, dtype=float)
        lexical = _minmax(lexical_raw)
        semantic = _minmax(semantic_raw)
        base = self.lexical_weight * lexical + self.semantic_weight * semantic
        rerank = np.asarray(
            [self._rerank_bonus(query, chunk) for chunk in self.chunks], dtype=float
        )
        combined = 0.88 * base + 0.12 * rerank
        ordered = np.argsort(combined)[::-1][: max(1, min(top_k, len(self.chunks)))]
        return [
            SearchHit(
                chunk=self.chunks[index],
                score=float(combined[index]),
                lexical_score=float(lexical[index]),
                semantic_score=float(semantic[index]),
                rerank_score=float(rerank[index]),
                rank=rank,
            )
            for rank, index in enumerate(ordered, start=1)
        ]

