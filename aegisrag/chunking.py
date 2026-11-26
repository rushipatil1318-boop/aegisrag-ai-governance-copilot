from __future__ import annotations

import hashlib
import re

from .schemas import Chunk, SourceDocument

HEADING_PATTERN = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)
SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")


def _stable_id(source_id: str, section: str, index: int, content: str) -> str:
    digest = hashlib.sha1(content.encode("utf-8")).hexdigest()[:10]
    return f"{source_id}:{index}:{digest}"


def _sections(content: str) -> list[tuple[str, str]]:
    matches = list(HEADING_PATTERN.finditer(content))
    if not matches:
        return [("Overview", content.strip())]
    result: list[tuple[str, str]] = []
    prefix = content[: matches[0].start()].strip()
    if prefix:
        result.append(("Overview", prefix))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        body = content[start:end].strip()
        if body:
            result.append((match.group(2).strip(), body))
    return result


def _window_sentences(text: str, max_words: int, overlap_sentences: int) -> list[str]:
    sentences = [part.strip() for part in SENTENCE_PATTERN.split(text) if part.strip()]
    if not sentences:
        return []
    windows: list[str] = []
    start = 0
    while start < len(sentences):
        selected: list[str] = []
        word_count = 0
        end = start
        while end < len(sentences):
            candidate_words = len(sentences[end].split())
            if selected and word_count + candidate_words > max_words:
                break
            selected.append(sentences[end])
            word_count += candidate_words
            end += 1
        windows.append(" ".join(selected))
        if end >= len(sentences):
            break
        start = max(start + 1, end - overlap_sentences)
    return windows


def chunk_documents(
    documents: list[SourceDocument], max_words: int = 180, overlap_sentences: int = 1
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        chunk_index = 0
        for section, body in _sections(document.content):
            for text in _window_sentences(body, max_words, overlap_sentences):
                chunks.append(
                    Chunk(
                        chunk_id=_stable_id(document.source_id, section, chunk_index, text),
                        source_id=document.source_id,
                        title=document.title,
                        section=section,
                        content=text,
                        framework=document.framework,
                        reference=document.reference,
                        source_url=document.source_url,
                        topics=document.topics,
                    )
                )
                chunk_index += 1
    return chunks

