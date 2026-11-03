from __future__ import annotations

import json

from aegisrag import AegisRAG


def main() -> None:
    rag = AegisRAG()
    print("AegisRAG runtime")
    print(json.dumps(rag.source_summary(), indent=2))
    print()
    answer = rag.ask("What controls are expected for a high-risk AI system?")
    print(answer.answer)
    print()
    for citation in answer.citations:
        print(f"[{citation.citation_id}] {citation.reference}: {citation.source_url}")


if __name__ == "__main__":
    main()

