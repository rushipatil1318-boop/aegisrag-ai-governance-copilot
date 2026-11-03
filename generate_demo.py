from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aegisrag import AegisRAG  # noqa: E402


def assessment_markdown(assessment: dict) -> str:
    lines = [
        f"# AI Governance Screening: {assessment['system_name']}",
        "",
        f"**Result:** {assessment['risk_level']}",
        f"**Confidence:** {assessment['confidence']:.0%}",
        f"**Trace ID:** `{assessment['trace_id']}`",
        "",
        "## Triggering factors",
        *[f"- {item}" for item in assessment["triggers"]],
        "",
        "## Likely obligations",
        *[f"- {item}" for item in assessment["likely_obligations"]],
        "",
        "## Identified control gaps",
        *[f"- {item}" for item in assessment["control_gaps"]],
        "",
        "## Recommended actions",
        *[f"- {item}" for item in assessment["recommended_actions"]],
        "",
        "## Evidence register",
    ]
    for citation in assessment["citations"]:
        lines.append(
            f"- [{citation['citation_id']}] [{citation['reference']}]({citation['source_url']}) — "
            f"{citation['title']}"
        )
    lines.extend(["", f"> {assessment['disclaimer']}", ""])
    return "\n".join(lines)


def main() -> None:
    rag = AegisRAG()
    sample_path = ROOT / "data" / "sample_systems" / "recruitment_assistant.json"
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    assessment = rag.assess(sample).to_dict()
    questions = [
        "Why can an AI recruitment ranking system be high-risk?",
        "Which controls should be documented before deployment?",
        "How should a team measure and manage AI risk using the NIST AI RMF?",
    ]
    answers = [rag.ask(question).to_dict() for question in questions]
    output_dir = ROOT / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sample_assessment.json").write_text(
        json.dumps(assessment, indent=2), encoding="utf-8"
    )
    (output_dir / "sample_audit_report.md").write_text(
        assessment_markdown(assessment), encoding="utf-8"
    )
    (output_dir / "demo_transcript.json").write_text(
        json.dumps(answers, indent=2), encoding="utf-8"
    )
    print(f"Generated demo artifacts in {output_dir}")


if __name__ == "__main__":
    main()

