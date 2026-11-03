from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .schemas import SourceDocument

REQUIRED_METADATA = {
    "source_id",
    "title",
    "framework",
    "reference",
    "source_url",
    "last_verified",
}


def _parse_frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        raise ValueError(f"Missing YAML frontmatter: {path}")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid YAML frontmatter: {path}")
    metadata = yaml.safe_load(parts[1]) or {}
    missing = REQUIRED_METADATA - set(metadata)
    if missing:
        raise ValueError(f"Missing metadata {sorted(missing)} in {path}")
    return metadata, parts[2].strip()


def load_documents(directory: Path) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    seen: set[str] = set()
    for path in sorted(directory.glob("*.md")):
        metadata, content = _parse_frontmatter(path.read_text(encoding="utf-8"), path)
        source_id = str(metadata["source_id"])
        if source_id in seen:
            raise ValueError(f"Duplicate source_id: {source_id}")
        seen.add(source_id)
        topics = tuple(str(topic) for topic in metadata.get("topics", []))
        documents.append(
            SourceDocument(
                source_id=source_id,
                title=str(metadata["title"]),
                content=content,
                framework=str(metadata["framework"]),
                reference=str(metadata["reference"]),
                source_url=str(metadata["source_url"]),
                last_verified=str(metadata["last_verified"]),
                topics=topics,
                metadata={k: v for k, v in metadata.items() if k not in REQUIRED_METADATA},
            )
        )
    if not documents:
        raise FileNotFoundError(f"No Markdown sources found in {directory}")
    return documents

