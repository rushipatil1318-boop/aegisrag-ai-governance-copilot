from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "AegisRAG_End_to_End.ipynb"
sys.path.insert(0, str(ROOT))


def build() -> nbformat.NotebookNode:
    notebook = nbformat.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    }
    notebook["cells"] = [
        nbformat.v4.new_markdown_cell(
            "# AegisRAG: End-to-End Generative AI Governance Copilot\n\n"
            "This executed notebook demonstrates source ingestion, hybrid retrieval, grounded "
            "generation, citation validation, AI risk screening, and evaluation."
        ),
        nbformat.v4.new_code_cell(
            "from pathlib import Path\n"
            "import json\n"
            "from aegisrag import AegisRAG\n"
            "from aegisrag.evaluation import evaluate\n\n"
            "ROOT = Path.cwd()\n"
            "rag = AegisRAG()\n"
            "print('AegisRAG initialised successfully')"
        ),
        nbformat.v4.new_markdown_cell("## 1. Source and runtime summary"),
        nbformat.v4.new_code_cell("print(json.dumps(rag.source_summary(), indent=2))"),
        nbformat.v4.new_markdown_cell("## 2. Hybrid retrieval with component scores"),
        nbformat.v4.new_code_cell(
            "query = 'What controls are expected for a high-risk AI system?'\n"
            "hits = rag.retriever.search(query, top_k=5)\n"
            "for hit in hits:\n"
            "    print(f'{hit.rank}. {hit.chunk.reference:24} score={hit.score:.3f} '"
            "          f'lexical={hit.lexical_score:.3f} semantic={hit.semantic_score:.3f}')"
        ),
        nbformat.v4.new_markdown_cell("## 3. Evidence-grounded answer with citations"),
        nbformat.v4.new_code_cell(
            "question = 'What transparency duties may apply to a customer-service chatbot?'\n"
            "answer = rag.ask(question)\n"
            "print(answer.answer)\n"
            "print(f'\\nConfidence: {answer.confidence:.1%}')\n"
            "print(f'Evidence quality: {answer.evidence_quality}')\n"
            "for citation in answer.citations:\n"
            "    print(f'[{citation.citation_id}] {citation.reference} -> {citation.source_url}')"
        ),
        nbformat.v4.new_markdown_cell("## 4. AI-system risk screening and control gaps"),
        nbformat.v4.new_code_cell(
            "profile_path = ROOT / 'data/sample_systems/recruitment_assistant.json'\n"
            "profile = json.loads(profile_path.read_text())\n"
            "assessment = rag.assess(profile)\n"
            "print(f'System: {assessment.system_name}')\n"
            "print(f'Result: {assessment.risk_level} ({assessment.confidence:.0%})')\n"
            "print('\\nTriggers:')\n"
            "for item in assessment.triggers: print('-', item)\n"
            "print('\\nControl gaps:')\n"
            "for item in assessment.control_gaps: print('-', item)"
        ),
        nbformat.v4.new_markdown_cell("## 5. Reproducible offline evaluation"),
        nbformat.v4.new_code_cell(
            "summary, rows = evaluate(rag)\n"
            "print(json.dumps(summary, indent=2))"
        ),
        nbformat.v4.new_markdown_cell(
            "## Result\n\n"
            "The complete pipeline runs without an external LLM key. Hosted or local LLMs can be "
            "enabled through environment variables while keeping retrieval, guardrails, citations, "
            "risk-screening, evaluation, and audit components unchanged."
        ),
    ]
    return notebook


def main() -> None:
    notebook = build()
    namespace = {"__name__": "__main__"}
    execution_count = 0
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        execution_count += 1
        stream = io.StringIO()
        try:
            with contextlib.redirect_stdout(stream):
                exec(compile(cell["source"], "<notebook-cell>", "exec"), namespace)
        except Exception:
            cell["execution_count"] = execution_count
            cell["outputs"] = [
                nbformat.v4.new_output(
                    "stream", name="stdout", text=stream.getvalue()
                )
            ]
            raise
        cell["execution_count"] = execution_count
        text = stream.getvalue()
        cell["outputs"] = (
            [nbformat.v4.new_output("stream", name="stdout", text=text)] if text else []
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, OUTPUT)
    print(f"Saved executed notebook to {OUTPUT}")


if __name__ == "__main__":
    main()

