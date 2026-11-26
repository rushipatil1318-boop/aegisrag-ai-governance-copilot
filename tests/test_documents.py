from aegisrag.chunking import chunk_documents
from aegisrag.config import settings
from aegisrag.documents import load_documents


def test_official_documents_load_with_unique_ids():
    documents = load_documents(settings.knowledge_base_dir)
    assert len(documents) >= 15
    assert len({document.source_id for document in documents}) == len(documents)
    assert all(document.source_url.startswith("https://") for document in documents)


def test_heading_aware_chunking_is_deterministic():
    documents = load_documents(settings.knowledge_base_dir)
    first = chunk_documents(documents)
    second = chunk_documents(documents)
    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
    assert len({chunk.chunk_id for chunk in first}) == len(first)
    assert all(chunk.section for chunk in first)

