from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


class EmbeddingBackend(Protocol):
    name: str

    def fit(self, texts: list[str]) -> np.ndarray: ...

    def encode_query(self, text: str) -> np.ndarray: ...


@dataclass
class LSAEmbeddingBackend:
    dimensions: int = 128
    name: str = "lsa-tfidf"

    def __post_init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), min_df=1, sublinear_tf=True
        )
        self.svd: TruncatedSVD | None = None

    def fit(self, texts: list[str]) -> np.ndarray:
        matrix = self.vectorizer.fit_transform(texts)
        max_components = min(self.dimensions, matrix.shape[0] - 1, matrix.shape[1] - 1)
        if max_components >= 2:
            self.svd = TruncatedSVD(n_components=max_components, random_state=42)
            vectors = self.svd.fit_transform(matrix)
        else:
            vectors = matrix.toarray()
        return normalize(vectors)

    def encode_query(self, text: str) -> np.ndarray:
        vector = self.vectorizer.transform([text])
        if self.svd is not None:
            vector = self.svd.transform(vector)
        else:
            vector = vector.toarray()
        return normalize(vector)[0]


class SentenceTransformerBackend:
    name = "sentence-transformers"

    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Install the dense extra with: pip install -e '.[dense]'"
            ) from exc
        self.model = SentenceTransformer(model_name)

    def fit(self, texts: list[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts, normalize_embeddings=True))

    def encode_query(self, text: str) -> np.ndarray:
        return np.asarray(self.model.encode([text], normalize_embeddings=True))[0]


def create_embedding_backend(name: str, model_name: str) -> EmbeddingBackend:
    if name in {"sentence-transformers", "dense", "minilm"}:
        return SentenceTransformerBackend(model_name)
    return LSAEmbeddingBackend()

