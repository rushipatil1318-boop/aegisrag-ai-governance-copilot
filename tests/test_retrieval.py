from dataclasses import replace

from aegisrag.config import settings
from aegisrag.orchestrator import AegisRAG


def build_rag(tmp_path):
    return AegisRAG(
        replace(
            settings,
            llm_provider="offline",
            embedding_backend="lsa",
            audit_log_path=tmp_path / "audit.jsonl",
        )
    )


def test_hybrid_retrieval_finds_recruitment_classification(tmp_path):
    rag = build_rag(tmp_path)
    hits = rag.retriever.search("job applicant recruitment ranking high-risk", top_k=5)
    assert "eu_article_6_annex_iii" in [hit.chunk.source_id for hit in hits]


def test_hybrid_retrieval_finds_nist_functions(tmp_path):
    rag = build_rag(tmp_path)
    hits = rag.retriever.search("NIST Govern Map Measure Manage functions", top_k=5)
    assert "nist_core" in [hit.chunk.source_id for hit in hits]


def test_scores_are_sorted(tmp_path):
    rag = build_rag(tmp_path)
    hits = rag.retriever.search("human oversight automation bias override", top_k=5)
    assert [hit.score for hit in hits] == sorted(
        [hit.score for hit in hits], reverse=True
    )

